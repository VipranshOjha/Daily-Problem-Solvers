# 🎨 String Art Portrait Generator

Ever wanted to turn a photo into a piece of handcrafted string art without doing complex math or spending hours planning the layout?

**Now you can. Automatically. Beautifully. And with a single piece of string.**

This tool takes a portrait image and transforms it into a **string art pattern**, generating the optimal connections between virtual nails placed around a circular frame. You just upload an image, and voilà – you get a canvas-friendly plan you can recreate in real life with nails and thread!

---

## 💡 Why I Built This

I love the idea of turning digital memories into something **tangible** and **creative** – but making string art manually? That takes serious patience, precision, and guesswork.

So I built this to:
- 📷 Convert portraits into thread patterns.
- 📐 Automatically place “nails” and calculate best connections.
- 🧠 Use image contrast and structure to plan the string paths.
- 🎁 Help anyone make **DIY gifts** or **home decor** from photos.

---

## 🖼️ What It Does

1. Upload a portrait image (your friend, your dog, your selfie).
2. The backend:
   - Preprocesses and enhances the image.
   - Places virtual nails around a circle.
   - Uses optimized logic to find best string connections.
3. The frontend:
   - Shows the progress live.
   - Renders the final **string art preview** on a canvas.
   - Gives you instructions to recreate it physically.

---

## 🧰 Technologies Used

- **Frontend**: HTML, TailwindCSS, JavaScript
- **Backend**: Python + Flask
- **Image Processing**: PIL, NumPy
- **Algorithm**: Optimized nail-pair selection + contribution scoring

---

## 🚀 How to Run

1. **Clone the repository** and navigate to the project folder:
   ```bash
   git clone https://github.com/VipranshOjha/Daily-Problem-Solvers
   cd Daily-Problem-Solvers/String-Art-Portrait-Generator
   ```

2. **Install backend dependencies**:

   ```bash
   pip install flask flask-cors pillow numpy
   ```

3. **Run the Flask API**:

   ```bash
   python Backend.py
   ```

4. **Open `index.html`** in your browser (no server needed for frontend).

Make sure the Flask API is running on `localhost:5000`.

---

## 📌 Recreate the Art in Real Life

Once you have the preview:

* 📍 Prepare a wooden board.
* 🔨 Hammer nails around the edge (as shown).
* 🧵 Tie string through them following the pattern.
* 💫 Watch your art come to life.

---

## 🧠 Behind the Scenes

Instead of checking **every possible line**, the backend uses:

* Smart nail-pair sampling
* Recent-connection filtering
* Contribution-based selection

This means it’s **fast**, **efficient**, and even works on lower-powered machines!

---

## ✨ Example Use Cases

* Make a **personalized handmade gift**.
* Turn your **pet’s face into string art**.
* Add a custom **art piece to your room**.
* Teach kids about math, geometry, and art – all in one!

---

## 📬 Like it? Have suggestions?

Feel free to open issues, contribute improvements, or just reach out. I’d love to see the art you make with this!

