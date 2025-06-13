import tkinter as tk
from tkinter import filedialog, messagebox
import os
import heapq
from collections import Counter

class Node:
    def __init__(self, char=None, freq=0):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

class HuffmanEncoder:
    def __init__(self):
        self.codes = {}
        self.reverse_codes = {}

    def build_frequency_dict(self, data):
        return Counter(data)

    def build_huffman_tree(self, freq_dict):
        heap = [Node(char, freq) for char, freq in freq_dict.items()]
        heapq.heapify(heap)

        while len(heap) > 1:
            left = heapq.heappop(heap)
            right = heapq.heappop(heap)
            merged = Node(freq=left.freq + right.freq)
            merged.left = left
            merged.right = right
            heapq.heappush(heap, merged)

        return heap[0] if heap else None

    def build_codes(self, root, current=""):
        if not root:
            return
        if root.char is not None:
            self.codes[root.char] = current
            self.reverse_codes[current] = root.char
            return
        self.build_codes(root.left, current + "0")
        self.build_codes(root.right, current + "1")

    def get_encoded_data(self, data):
        return ''.join(self.codes[byte] for byte in data)

    def pad_encoded_data(self, encoded_data):
        extra_padding = 8 - len(encoded_data) % 8
        encoded_data += "0" * extra_padding
        padded_info = f"{extra_padding:08b}"
        return padded_info + encoded_data

    def get_byte_array(self, padded_data):
        return bytearray(int(padded_data[i:i+8], 2) for i in range(0, len(padded_data), 8))

    def encode_file(self, source_file, dest_file):
        if not os.path.exists(source_file):
            raise FileNotFoundError("Source file does not exist")

        with open(source_file, "rb") as f:
            data = f.read()

        freq_dict = self.build_frequency_dict(data)
        root = self.build_huffman_tree(freq_dict)
        self.build_codes(root)

        encoded_data = self.get_encoded_data(data)
        padded_data = self.pad_encoded_data(encoded_data)
        byte_array = self.get_byte_array(padded_data)

        with open(dest_file, "wb") as f:
            f.write(byte_array)

        print("File encoded and saved successfully.")

    def remove_padding(self, padded_data):
        padded_info = padded_data[:8]
        extra_padding = int(padded_info, 2)
        return padded_data[8:-extra_padding] if extra_padding != 0 else padded_data[8:]

    def decode_data(self, encoded_data):
        current_code = ""
        decoded_bytes = bytearray()

        for bit in encoded_data:
            current_code += bit
            if current_code in self.reverse_codes:
                decoded_bytes.append(self.reverse_codes[current_code])
                current_code = ""

        return decoded_bytes

    def decode_file(self, source_file, dest_file):
        if not os.path.exists(source_file):
            raise FileNotFoundError("Compressed file not found")

        with open(source_file, "rb") as f:
            bit_string = ""
            byte = f.read(1)
            while byte:
                bits = bin(int.from_bytes(byte, 'big'))[2:].rjust(8, '0')
                bit_string += bits
                byte = f.read(1)

        actual_data = self.remove_padding(bit_string)
        decoded_bytes = self.decode_data(actual_data)

        with open(dest_file, "wb") as f:
            f.write(decoded_bytes)

        print("Decompression completed successfully.")

class HuffmanApp:
    def __init__(self, master):
        self.master = master
        master.title("Huffman Encoder/Decoder")
        master.geometry("400x200")

        self.encoder = HuffmanEncoder()

        self.label = tk.Label(master, text="Select a file to encode or decode")
        self.label.pack(pady=10)

        self.encode_btn = tk.Button(master, text="Encode File", command=self.encode_file)
        self.encode_btn.pack(pady=5)

        self.decode_btn = tk.Button(master, text="Decode File", command=self.decode_file)
        self.decode_btn.pack(pady=5)

        self.quit_btn = tk.Button(master, text="Exit", command=master.quit)
        self.quit_btn.pack(pady=10)

    def encode_file(self):
        source = filedialog.askopenfilename(
            title="Select File to Encode",
            filetypes=[("All Files", "*.*"), ("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")]
        )
        if not source:
            return

        dest = filedialog.asksaveasfilename(
            title="Save Encoded File As",
            defaultextension=".bin",
            filetypes=[("Binary Encoded Files", "*.bin"), ("All Files", "*.*")]
        )
        if not dest:
            return

        try:
            self.encoder.encode_file(source, dest)
            messagebox.showinfo("Success", "File encoded and saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def decode_file(self):
        source = filedialog.askopenfilename(
            title="Select Encoded File to Decode",
            filetypes=[("Binary Encoded Files", "*.bin"), ("All Files", "*.*")]
        )
        if not source:
            return

        dest = filedialog.asksaveasfilename(
            title="Save Decoded File As",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp"), ("All Files", "*.*")]
        )
        if not dest:
            return

        try:
            self.encoder.decode_file(source, dest)
            messagebox.showinfo("Success", "File decoded and saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = HuffmanApp(root)
    root.mainloop()
