# 🖼️ Super-Resolution – Image Enhancement Tool

A simple yet powerful tool that sharpens and enhances low-resolution images using the **Real-ESRGAN** deep learning model.

---

## 💡 Why I Built This

I created this as a daily problem-solving tool — we often deal with images that are blurry, low-resolution, or need enhancement before use. This tool helps improve image quality in seconds, and is especially useful for professionals, students, and content creators.

---

## 📌 Overview

Have a blurry or pixelated image you want to improve?

This project allows you to **enhance and upscale images by 4x**, restoring details and improving sharpness — useful for daily tasks like:

* Fixing low-quality downloaded images
* Restoring old or scanned photographs
* Improving images before printing or sharing
* Enhancing visuals for presentations and content creation

Built using **Real-ESRGAN**, a state-of-the-art super-resolution model for real-world image restoration.

---

## 🚀 Features

* 📈 4× upscaling for sharper, high-resolution images
* 🧠 Real-ESRGAN model integration
* 🖥️ Automatically detects GPU (CUDA) if available
* 📷 Side-by-side preview of original and enhanced image
* 💾 Option to save enhanced output

---

## 🛠️ How to Use

1. **Install dependencies**

   ```bash
   pip install realesrgan matplotlib pillow torch
   ```

2. **Run the script**

   ```bash
   python super_resolution.py
   ```

3. **Provide the image path**
   You'll be prompted to enter the image file path in the terminal.

4. **View results & save if desired**

---

## 🧰 Tech Stack

* Python
* PyTorch
* Real-ESRGAN
* PIL (Pillow)
* Matplotlib

---
