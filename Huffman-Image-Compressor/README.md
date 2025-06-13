# 🗜️ Huffman Image Compressor

A simple image compression and decompression tool using the Huffman Coding algorithm. Built with Python and Tkinter, this project was created out of necessity — to transfer a large number of image files while dealing with limited storage space
— but it works seamlessly with **any file type**, including text documents, PDFs, and more.

## 🚀 Features

- Compresses any file using Huffman encoding (optimized for images).
- Decompresses `.bin` files back to original format.
- Simple and intuitive GUI using Tkinter.
- Supports common formats like - `.png`, `.jpg`, `.jpeg`, `.bmp`, `.txt`, `.pdf`, `.doc`, and more.
  
## 🧠 Why I Built This

I needed to transfer a lot of image files but didn't have enough space. Instead of relying on external tools, I built this image compressor using the Huffman algorithm — an efficient, lossless compression method.

## 🖼️ How It Works

1. **Encoding (Compression)**
   - Reads file bytes.
   - Builds a frequency dictionary and Huffman Tree.
   - Encodes the content and writes the binary output to a `.bin` file.

2. **Decoding (Decompression)**
   - Reads the `.bin` file.
   - Reconstructs original binary data using the stored Huffman codes.
   - Restores the original image or file.

## 🛠️ Usage

1. **Run the Application**
   ```bash
   python Huffman.py
   ```
2. **Use the GUI**

   * Click **"Encode File"** to compress an image.
   * Click **"Decode File"** to restore a compressed file.
   * Output will be saved to the location you choose.

## 🐍 Tech Stack

* Python 3
* Tkinter (for GUI)
* Huffman Coding (Custom implementation)

## 📂 Supported Formats

Any file can be compressed and restored, including:

Images: .jpg, .png, .jpeg, .bmp

Documents: .txt, .pdf, .docx, .doc

Other formats: .mp3, .csv, .log, .zip, etc.

✅ Note: Compression efficiency may vary depending on file type.

---

Made with 💻 and Huffman Trees by Vipransh Ojha
