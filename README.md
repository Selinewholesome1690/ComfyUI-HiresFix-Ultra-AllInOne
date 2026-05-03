# 🎨 ComfyUI-HiresFix-Ultra-AllInOne - Improve AI Image Quality With Ease

[![Download ComfyUI-HiresFix-Ultra-AllInOne](https://img.shields.io/badge/Download-Click_Here-blue.svg)](https://github.com/Selinewholesome1690/ComfyUI-HiresFix-Ultra-AllInOne)

## 📦 About This Tool
This node simplifies the high-resolution image process for ComfyUI. Many users struggle to balance image details and scale. This tool combines several complex steps into one system. It handles model upscaling, latent upscaling, tiled VAE, and color correction. You gain clear, high-quality images without manual adjustments or multiple loose nodes. It works directly within your existing ComfyUI workflow.

## 💻 System Requirements
To run this software, ensure your computer meets these standards:
- Operating System: Windows 10 or Windows 11.
- Graphics Card: NVIDIA GPU with at least 8GB of video memory (VRAM).
- Memory: 16GB of system RAM.
- Software: A functioning installation of ComfyUI.
- Storage: 500MB of free disk space for local models and node files.

## 📥 How To Install
Follow these steps to add the tool to your computer.

1. Visit this page to download: [https://github.com/Selinewholesome1690/ComfyUI-HiresFix-Ultra-AllInOne](https://github.com/Selinewholesome1690/ComfyUI-HiresFix-Ultra-AllInOne).
2. Locate the green button labeled Code and select Download ZIP.
3. Save the folder to your desktop.
4. Extract the contents of the ZIP folder.
5. Open your ComfyUI installation folder.
6. Navigate to the folder named custom_nodes.
7. Move the extracted folder into the custom_nodes directory.
8. Restart ComfyUI to load the changes.

## 🛠️ Usage Instructions
Once the installation finishes, open your ComfyUI browser tab.

1. Right-click on the main canvas screen.
2. Select Add Node.
3. Find the category named Hires Fix Ultra.
4. Select the main node from the list.
5. Connect your existing model output to the new node input.
6. Connect the latent output of your sampling node to the input of the Hires Fix node.
7. Adjust the upscale factor slider to your preferred size.
8. Use the color correction toggle if your images appear too dark or bright after scaling.
9. Link the output of the node to your VAE Decode node.
10. Queue your prompt to start the process.

## ⚙️ Understanding Features
The node performs four main tasks. 

**Model Upscaling**
It uses high-end models to increase the sharpness of your art. It fills in missing pixel information during the resize stage. 

**Latent Upscaling**
This process happens early in the generation cycle. It creates a larger canvas for the AI to fill with details. This leads to better textures than simple resizing methods.

**Tiled VAE**
Some images consume too much video memory during the decode phase. The tiled VAE splits the final step into small segments. This prevents out-of-memory errors on mid-range graphics cards.

**Deep Histogram Color Correction**
Upscaling often shifts the color balance of an image. This tool analyzes the original colors and applies a correction layer. You get consistent results regardless of the upscale factor.

## 💡 Troubleshooting
If you encounter issues, review these common fixes.

**Node Does Not Appear**
Check that you placed the folder inside custom_nodes and not in the main directory. Confirm that you restarted the ComfyUI server window after moving the files.

**Out of Memory Error**
Lower your upscale factor. Ensure no other heavy applications run in the background. Use the Tiled VAE setting to reduce memory usage during output.

**Slow Generation Speed**
The tiling process adds time to the generation. If the speed is too slow, adjust the tiling overlap settings in the node configuration menu. 

**Color Shifts**
If the colors look wrong, click the bypass check on the color correction section of the node. This allows you to verify if the model upscale or the color correction creates the unwanted effect.

## 📝 Configuration Tips
- Start with a 1.5x upscale factor to test performance.
- Use the preview function to see the result before the final VAE decode happens.
- Ensure your model weights match the scale of the image you want.
- Use the advanced settings menu to change the interpolation method. Bicubic often results in softer images, while Lanczos provides sharp edges. 

## 📂 Project Metadata
- Topics: ai-art, color-correction, comfyui, comfyui-custom-node, hires-fix, latent-upscale, stable-diffusion, upscale, upscaling.
- License: Open Source.
- Support: Use the Issues tab on the repository page to report bugs. Provide your logs and a screenshot of your node wiring to get the fastest assistance.