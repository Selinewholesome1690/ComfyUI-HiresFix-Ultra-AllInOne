import torch
import torch.nn.functional as F
import comfy.samplers
import comfy.utils
import nodes
import comfy_extras.nodes_upscale_model

class HiresFixUltraAllInOne:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "model": ("MODEL",),
                "vae": ("VAE",),
                "upscale_method": ([
                    "Model", 
                    "Latent (Bicubic Antialiased)", 
                    "Latent (Bislerp)", 
                    "Latent (Nearest-Exact)", 
                    "Latent (Bicubic)", 
                    "Latent (Area)", 
                    "Latent (Bilinear Antialiased)"
                ], {"default": "Model"}),
                "positive": ("CONDITIONING",),
                "negative": ("CONDITIONING",),
                "upscale_by": ("FLOAT", {"default": 1.5, "min": 0.1, "max": 4.0, "step": 0.1}),
                "denoise": ("FLOAT", {"default": 0.35, "min": 0.0, "max": 1.0, "step": 0.01}),
                "steps": ("INT", {"default": 20, "min": 1, "max": 100}),
                "cfg": ("FLOAT", {"default": 5.0, "min": 0.0, "max": 100.0}),
                "sampler_name": (comfy.samplers.KSampler.SAMPLERS, ),
                "scheduler": (comfy.samplers.KSampler.SCHEDULERS, ),
                "seed": ("INT", {"default": 1234, "min": 0, "max": 0xffffffffffffffff}),
                "tile_size_vae": ("INT", {"default": 1024, "min": 256, "max": 4096, "step": 64}),
                "overlap": ("INT", {"default": 64, "min": 0, "max": 512, "step": 8}),
                "color_fix_type": (["None", "Standard", "Deep Histogram"], {"default": "Deep Histogram"}),
                "color_fix_strength": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.05}),
            },
            "optional": {
                "upscale_model": ("UPSCALE_MODEL",),
            }
        }

    RETURN_TYPES = ("IMAGE", "LATENT")
    RETURN_NAMES = ("image", "latent")
    FUNCTION = "execute"
    CATEGORY = "Image/Upscaling"

    def bislerp(self, samples, width, height):
        return F.interpolate(samples, size=(height, width), mode="bilinear", align_corners=False)

    def histogram_matching(self, target, source):
        B, C, H, W = target.shape
        target_mod = target + torch.randn_like(target) * 0.001
        target_flat = target_mod.view(B, C, -1)
        source_flat = source.view(B, C, -1)
        matched_flat = torch.zeros_like(target_flat)
        for b in range(B):
            for c in range(C):
                t_chan, s_chan = target_flat[b, c], source_flat[b, c]
                t_sorted, t_indices = torch.sort(t_chan)
                s_sorted, _ = torch.sort(s_chan)
                s_interp = F.interpolate(s_sorted.view(1, 1, -1), size=(t_chan.shape[0]), mode='linear', align_corners=False)
                matched_flat[b, c].scatter_(0, t_indices, s_interp.view(-1))
        return matched_flat.view(B, C, H, W)

    def apply_color_fix(self, target, source, fix_type, strength):
        if fix_type == "None" or strength <= 0: return target
        device = target.device
        t_p, s_p = target.permute(0, 3, 1, 2).to(device), source.permute(0, 3, 1, 2).to(device)
        s_p_resized = F.interpolate(s_p, size=(t_p.shape[2], t_p.shape[3]), mode='bicubic', align_corners=False)
        
        if fix_type == "Standard":
            mu_t, std_t = t_p.mean(dim=(2,3), keepdim=True), t_p.std(dim=(2,3), keepdim=True)
            mu_s, std_s = s_p_resized.mean(dim=(2,3), keepdim=True), s_p_resized.std(dim=(2,3), keepdim=True)
            result = (t_p - mu_t) * (std_s / (std_t + 1e-5)) + mu_s
        elif fix_type == "Deep Histogram":
            result = self.histogram_matching(t_p, s_p_resized)
        else: result = t_p
        
        result = torch.lerp(t_p, result, strength)
        return torch.clamp(result, 0.0, 1.0).permute(0, 2, 3, 1)

    def execute(self, image, model, vae, upscale_method, positive, negative,
                upscale_by, denoise, steps, cfg, sampler_name, scheduler,
                seed, tile_size_vae, overlap, color_fix_type, color_fix_strength, upscale_model=None):

        B, H, W, C = image.shape
        target_w, target_h = int((W * upscale_by) // 8) * 8, int((H * upscale_by) // 8) * 8

        # --- 1. UPSCALE ---
        if "Model" in upscale_method:
            if upscale_model is None:
                raise ValueError("Connect the Upscale Model to the input!")
            upscale_node = comfy_extras.nodes_upscale_model.ImageUpscaleWithModel()
            upscaled_pixel = upscale_node.upscale(upscale_model, image)[0]
            upscaled_pixel = F.interpolate(upscaled_pixel.permute(0, 3, 1, 2), size=(target_h, target_w), mode='bicubic', align_corners=False).permute(0, 2, 3, 1)
            latent_samples = vae.encode_tiled(upscaled_pixel[:,:,:,:3], tile_x=tile_size_vae, tile_y=tile_size_vae, overlap=overlap)
        else:
            latents = vae.encode_tiled(image[:,:,:,:3], tile_x=tile_size_vae, tile_y=tile_size_vae, overlap=overlap)
            if "Bislerp" in upscale_method:
                latent_samples = self.bislerp(latents, target_w // 8, target_h // 8)
            else:
                antialias = "Antialiased" in upscale_method
                if "Nearest-Exact" in upscale_method: mode = "nearest-exact"
                elif "Area" in upscale_method: mode = "area"
                elif "Bilinear" in upscale_method: mode = "bilinear"
                else: mode = "bicubic"
                latent_samples = F.interpolate(latents, size=(target_h // 8, target_w // 8), mode=mode, antialias=antialias)

        # --- 2. SAMPLING ---
        sampled_latent = nodes.common_ksampler(
            model, seed, steps, cfg, sampler_name, scheduler, 
            positive, negative, {"samples": latent_samples}, denoise=denoise
        )[0]

        # --- 3. DECODE ---
        decoded_image = vae.decode_tiled(sampled_latent["samples"], tile_x=tile_size_vae, tile_y=tile_size_vae, overlap=overlap)
        
        # --- 4. COLOR FIX ---
        final_image = self.apply_color_fix(decoded_image, image, color_fix_type, color_fix_strength)

        # Возвращаем изображение и латент (в формате словаря ComfyUI)
        return (final_image, sampled_latent)

NODE_CLASS_MAPPINGS = {"HiresFixUltraAllInOne": HiresFixUltraAllInOne}
NODE_DISPLAY_NAME_MAPPINGS = {"HiresFixUltraAllInOne": "Hires Fix Ultra - All in One"}