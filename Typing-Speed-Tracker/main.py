import tkinter as tk
import random
import time

TEXTS = [
    "The quick brown fox jumps over the lazy dog",
    "Typing fast requires accuracy and practice",
    "Python is powerful and easy to learn",
    "Artificial intelligence is shaping the future",
    "Consistency beats talent when talent is inconsistent"
]

class TypingSpeedApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Typing Speed Tracker")
        self.root.geometry("900x620")

        self.test_mode = tk.StringVar(value="60s")
        self.strict_mode = tk.BooleanVar(value=True)
        self.dark_mode = False

        self.reset_test()
        self.build_ui()
        self.apply_theme()

    def reset_test(self):
        self.text = random.choice(TEXTS)
        self.start_time = None
        self.running = False

        self.correct_chars = 0
        self.total_typed = 0
        self.mistake_positions = set()
        self.wpm_history = []

    def build_ui(self):
        self.header = tk.Label(self.root, text="Typing Speed Test",
                               font=("Arial", 20, "bold"))
        self.header.pack(pady=5)

        controls = tk.Frame(self.root)
        controls.pack(pady=5)

        tk.Label(controls, text="Mode:").grid(row=0, column=0, padx=5)
        tk.OptionMenu(controls, self.test_mode, "30s", "60s", "25 words").grid(row=0, column=1)

        tk.Checkbutton(controls, text="Strict Mode",
                       variable=self.strict_mode).grid(row=0, column=2, padx=10)

        tk.Button(controls, text="🌙 / ☀️ Theme",
                  command=self.toggle_theme).grid(row=0, column=3, padx=10)

        tk.Button(controls, text="Restart",
                  command=self.restart).grid(row=0, column=4, padx=10)

        self.prompt = tk.Text(self.root, height=3, wrap="word",
                              font=("Consolas", 14), relief="flat")
        self.prompt.pack(padx=10, pady=10, fill="x")
        self.prompt.insert("1.0", self.text)
        self.prompt.config(state="disabled")

        self.prompt.tag_config("correct")
        self.prompt.tag_config("wrong")
        self.prompt.tag_config("pending")

        self.input_box = tk.Text(self.root, height=4, font=("Consolas", 14))
        self.input_box.pack(padx=10, pady=10, fill="x")
        self.input_box.bind("<KeyRelease>", self.on_type)

        self.stats = tk.Label(self.root, text="WPM: 0 | Accuracy: 0%",
                              font=("Arial", 14))
        self.stats.pack()

        self.timer_label = tk.Label(self.root, text="Waiting...",
                                    font=("Arial", 14))
        self.timer_label.pack(pady=5)

        self.graph = tk.Canvas(self.root, width=860, height=150)
        self.graph.pack(pady=10)

    def on_type(self, event):
        if not self.running:
            self.start_test()

        typed = self.input_box.get("1.0", "end-1c")
        self.total_typed = len(typed)
        self.correct_chars = 0

        self.update_prompt_colors(typed)
        self.update_stats()

        if self.test_mode.get() == "25 words":
            if len(typed.split()) >= 25:
                self.end_test()

    def update_prompt_colors(self, typed):
        self.prompt.config(state="normal")
        self.prompt.tag_remove("correct", "1.0", "end")
        self.prompt.tag_remove("wrong", "1.0", "end")
        self.prompt.tag_remove("pending", "1.0", "end")

        for i, char in enumerate(self.text):
            idx = f"1.{i}"

            if i < len(typed):
                if typed[i] == char and i not in self.mistake_positions:
                    self.prompt.tag_add("correct", idx)
                    self.correct_chars += 1
                else:
                    self.prompt.tag_add("wrong", idx)
                    if self.strict_mode.get():
                        self.mistake_positions.add(i)
            else:
                self.prompt.tag_add("pending", idx)

        self.prompt.config(state="disabled")

    def start_test(self):
        self.running = True
        self.start_time = time.time()
        self.update_timer()
        self.update_graph()

    def update_timer(self):
        if not self.running:
            return

        if self.test_mode.get() in ["30s", "60s"]:
            duration = 30 if self.test_mode.get() == "30s" else 60
            elapsed = int(time.time() - self.start_time)
            remaining = duration - elapsed

            if remaining <= 0:
                self.end_test()
                return

            self.timer_label.config(text=f"Time Left: {remaining}s")
            self.root.after(1000, self.update_timer)
        else:
            self.timer_label.config(text="Word Mode")

    def update_stats(self):
        elapsed = max(time.time() - self.start_time, 1)
        minutes = elapsed / 60

        wpm = int((self.correct_chars / 5) / minutes)
        accuracy = int((self.correct_chars /
                        max(self.total_typed, 1)) * 100)

        self.stats.config(text=f"WPM: {wpm} | Accuracy: {accuracy}%")

    def update_graph(self):
        if not self.running:
            return

        elapsed = max(time.time() - self.start_time, 1)
        minutes = elapsed / 60
        wpm = int((self.correct_chars / 5) / minutes)

        self.wpm_history.append(wpm)
        self.draw_graph()

        self.root.after(1000, self.update_graph)

    def draw_graph(self):
        self.graph.delete("all")
        if len(self.wpm_history) < 2:
            return

        max_wpm = max(self.wpm_history) + 5
        w, h = 860, 150
        step = w / (len(self.wpm_history) - 1)

        for i in range(len(self.wpm_history) - 1):
            x1 = i * step
            y1 = h - (self.wpm_history[i] / max_wpm) * h
            x2 = (i + 1) * step
            y2 = h - (self.wpm_history[i + 1] / max_wpm) * h
            self.graph.create_line(x1, y1, x2, y2, width=2)

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()

    def apply_theme(self):
        bg = "#121212" if self.dark_mode else "#f5f5f5"
        fg = "#ffffff" if self.dark_mode else "#000000"

        self.root.config(bg=bg)
        for widget in self.root.winfo_children():
            try:
                widget.config(bg=bg, fg=fg)
            except:
                pass

        self.prompt.config(bg="#1e1e1e" if self.dark_mode else "#ffffff",
                           fg=fg)
        self.input_box.config(bg="#1e1e1e" if self.dark_mode else "#ffffff",
                              fg=fg)
        self.graph.config(bg="#1e1e1e" if self.dark_mode else "#ffffff")

        self.prompt.tag_config("correct", foreground="#00ff88")
        self.prompt.tag_config("wrong", foreground="#ff5555")
        self.prompt.tag_config("pending", foreground="#888888")

    def end_test(self):
        self.running = False
        self.input_box.config(state="disabled")
        self.timer_label.config(text="Test Finished ⏹️")

    def restart(self):
        self.reset_test()
        self.input_box.config(state="normal")
        self.input_box.delete("1.0", "end")
        self.prompt.config(state="normal")
        self.prompt.delete("1.0", "end")
        self.prompt.insert("1.0", self.text)
        self.prompt.config(state="disabled")
        self.stats.config(text="WPM: 0 | Accuracy: 0%")
        self.timer_label.config(text="Waiting...")
        self.graph.delete("all")

if __name__ == "__main__":
    root = tk.Tk()
    app = TypingSpeedApp(root)
    root.mainloop()
