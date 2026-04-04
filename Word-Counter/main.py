import tkinter as tk
import re

class WordCounterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Word Counter - Neo-Brutalist")
        self.root.geometry("1100x700")
        self.root.configure(bg="#ffffff")
        
        # State
        self.include_spaces = tk.BooleanVar(value=True)

        self.create_widgets()
        
    def make_brutalist(self, parent, is_button=False, bg_color="#9a7bb2", text="", font=("Arial Black", 14, "bold"), fg="black", command=None, anchor="center"):
        container = tk.Frame(parent, bg="#ffffff")
        shadow = tk.Frame(container, bg="black")
        shadow.place(x=6, y=6, relwidth=1, relheight=1, width=-6, height=-6)
        
        if is_button:
            el = tk.Button(container, text=text, bg=bg_color, fg=fg, font=font, bd=4, relief="solid", command=command, activebackground=bg_color, anchor=anchor, cursor="hand2")
        else:
            el = tk.Label(container, text=text, bg=bg_color, fg=fg, font=font, bd=4, relief="solid", anchor=anchor)
            
        el.pack(padx=(0, 6), pady=(0, 6), fill=tk.BOTH, expand=True)
        return container, el
        
    def make_brutalist_text(self, parent):
        container = tk.Frame(parent, bg="#ffffff")
        shadow = tk.Frame(container, bg="black")
        shadow.place(x=6, y=6, relwidth=1, relheight=1, width=-6, height=-6)
        
        el = tk.Text(container, bg="#ffffff", fg="#000000", insertbackground="black", font=("Courier New", 16, "bold"), bd=4, relief="solid", wrap=tk.WORD, padx=15, pady=15)
        el.pack(padx=(0, 6), pady=(0, 6), fill=tk.BOTH, expand=True)
        return container, el

    def create_widgets(self):
        # Header Container
        header_frame = tk.Frame(self.root, bg="#ffffff")
        header_frame.pack(fill=tk.X, padx=40, pady=(40, 20))
        
        # The main title aligned left-to-center
        self.header_cont, self.header_lbl = self.make_brutalist(header_frame, bg_color="#9a7bb2", text="WORD COUNTER APP", font=("Arial Black", 32, "bold"))
        self.header_lbl.configure(padx=20, pady=10)
        self.header_cont.pack()
        
        # Lower content area 
        content_frame = tk.Frame(self.root, bg="#ffffff")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=(0, 40))
        
        # Left sidebar for buttons
        sidebar = tk.Frame(content_frame, bg="#ffffff", width=220)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 30))
        
        button_font = ("Arial Black", 14, "bold")
        
        self.btn_spaces_cont, self.btn_spaces = self.make_brutalist(sidebar, is_button=True, text="SPACES: ON", font=button_font, anchor="w", command=self.toggle_spaces)
        self.btn_spaces.configure(padx=10, pady=5)
        self.btn_spaces_cont.pack(fill=tk.X, pady=(0, 15))
        
        self.btn_paste_cont, self.btn_paste = self.make_brutalist(sidebar, is_button=True, text="PASTE TEXT", font=button_font, anchor="w", command=self.paste_text)
        self.btn_paste.configure(padx=10, pady=5)
        self.btn_paste_cont.pack(fill=tk.X, pady=(0, 15))
        
        self.btn_clear_cont, self.btn_clear = self.make_brutalist(sidebar, is_button=True, text="CLEARALL", font=button_font, anchor="w", command=self.clear_text)
        self.btn_clear.configure(padx=10, pady=5)
        self.btn_clear_cont.pack(fill=tk.X, pady=(0, 15))
        
        self.btn_copy_cont, self.btn_copy = self.make_brutalist(sidebar, is_button=True, text="COPY STATS", font=button_font, anchor="w", command=self.copy_results)
        self.btn_copy.configure(padx=10, pady=5)
        self.btn_copy_cont.pack(fill=tk.X, pady=(0, 15))

        # Main context area
        main_area = tk.Frame(content_frame, bg="#ffffff")
        main_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Text input setup - making it look like a "raw interface"
        self.text_cont, self.text_input = self.make_brutalist_text(main_area)
        self.text_cont.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Add instruction text to empty text box
        self.text_input.insert("1.0", "Paste or type your text here to expose true analytics...")
        self.text_input.configure(fg="#aaaaaa")
        
        # Clear placeholder on first click
        self.text_input.bind("<Button-1>", self.clear_placeholder)
        self.text_input.bind("<KeyRelease>", self.analyze_text)
        
        # Second lower text box placeholder (removed to simplify, we use a single big stats bar)
        
        # Stat row
        stat_font = ("Arial Black", 14, "bold")
        self.stats_cont, self.stats_lbl = self.make_brutalist(main_area, bg_color="#9a7bb2", text="W: 0    C: 0    S: 0    P: 0", font=stat_font, anchor="w")
        self.stats_lbl.configure(padx=20, pady=10)
        self.stats_cont.pack(fill=tk.X)
        
        # Save placeholder state
        self.placeholder_active = True

    def clear_placeholder(self, event=None):
        if self.placeholder_active:
            self.text_input.delete("1.0", tk.END)
            self.text_input.configure(fg="#000000")
            self.placeholder_active = False

    def toggle_spaces(self):
        self.include_spaces.set(not self.include_spaces.get())
        if self.include_spaces.get():
            self.btn_spaces.configure(text="SPACES: ON")
        else:
            self.btn_spaces.configure(text="SPACES: OFF")
        self.analyze_text()
        
    def paste_text(self):
        try:
            content = self.root.clipboard_get()
            self.clear_placeholder()
            self.text_input.insert(tk.INSERT, content)
            self.analyze_text()
        except tk.TclError:
            print("Clipboard empty")
            
    def clear_text(self):
        self.text_input.delete("1.0", tk.END)
        self.placeholder_active = True
        self.text_input.insert("1.0", "Paste or type your text here to expose true analytics...")
        self.text_input.configure(fg="#aaaaaa")
        self.analyze_text()
        
    def copy_results(self):
        # We need to analyze first in case the user typed without spaces
        self.analyze_text()
        text = self.stats_lbl.cget("text")
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        
    def analyze_text(self, event=None):
        if self.placeholder_active and event is not None and event.keysym not in ("Shift_L", "Shift_R", "Control_L", "Control_R", "Alt_L", "Alt_R", "Tab"):
             # Once the user types anything, mark placeholder inactive and color it black
             self.placeholder_active = False
             self.text_input.configure(fg="#000000")
             
        if self.placeholder_active:
            self.stats_lbl.configure(text="WORDS: 0    CHARS: 0    SENTS: 0    PARAS: 0")
            return
            
        text = self.text_input.get("1.0", "end-1c")
        
        if not text.strip():
            self.stats_lbl.configure(text="WORDS: 0    CHARS: 0    SENTS: 0    PARAS: 0")
            return
            
        # Character count
        if self.include_spaces.get():
            char_count = len(text)
        else:
            char_count = len(re.sub(r'\s+', '', text))
            
        # Word count
        words = [w for w in text.split() if re.search(r'\w', w)]
        word_count = len(words)
        
        # Sentence count
        sentences = [s for s in re.split(r'[.!?]+', text) if re.search(r'\w', s)]
        sent_count = len(sentences)
        
        # Paragraph count
        paragraphs = [p for p in re.split(r'\n+', text) if re.search(r'\w', p)]
        para_count = len(paragraphs)
        
        res = f"WORDS: {word_count}    CHARS: {char_count}    SENTS: {sent_count}    PARAS: {para_count}"
        self.stats_lbl.configure(text=res)

if __name__ == "__main__":
    root = tk.Tk()
    app = WordCounterApp(root)
    root.mainloop()
