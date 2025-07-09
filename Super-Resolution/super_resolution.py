from PIL import Image
import matplotlib.pyplot as plt
from realesrgan import RealESRGAN
import torch
import os

def enhance_image(img_path):
    if not os.path.exists(img_path):
        print(f"❌ File not found: {img_path}")
        return

    # Load image
    image = Image.open(img_path).convert("RGB")

    # Select device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"🚀 Using device: {device}")

    # Load Real-ESRGAN model
    model = RealESRGAN(device, scale=4)
    model.load_weights('RealESRGAN_x4.pth')  # Automatically downloads

    # Enhance
    print("🧠 Enhancing image...")
    sr_image = model.predict(image)

    # Show both images
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    plt.title("Original Image")
    plt.imshow(image)
    plt.axis('off')

    plt.subplot(1, 2, 2)
    plt.title("Enhanced Image")
    plt.imshow(sr_image)
    plt.axis('off')
    plt.tight_layout()
    plt.show()

    # Ask to save
    save = input("💾 Save the enhanced image? (y/n): ").strip().lower()
    if save == 'y':
        out_path = os.path.splitext(img_path)[0] + "_enhanced.png"
        sr_image.save(out_path)
        print(f"✅ Saved to {out_path}")

if __name__ == '__main__':
    img_path = input("📂 Enter the image file path: ").strip()
    enhance_image(img_path)
