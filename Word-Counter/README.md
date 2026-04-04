# Word Counter 🧮

A desktop word counting and text analytics application built using Python and Tkinter.  
This tool provides real-time insights into your writing — including word count, character count, sentence structure, and paragraph breakdown — without requiring internet access or external tools.

---

## Why I Built This

While writing documentation, assignments, and project descriptions, I noticed how often I needed a quick word count.

The usual workflow was:

- Open a browser  
- Search for a word counter  
- Paste text into a website  
- Get distracted before finishing the task

Most online tools felt unnecessarily heavy for such a simple need — filled with ads, slow loading times, or features unrelated to the actual goal.

I built this project to:

- Create a **fast offline word counter** I could open instantly
- Understand real-time text analysis using event-driven GUI updates
- Practice building structured desktop interfaces in Tkinter
- Solve a small daily friction in my writing workflow

This project focuses on simplicity: type text → instantly understand it.

---

## Features

### 📊 Real-Time Text Statistics

Live updates while typing:

- Word Count
- Character Count
- Sentence Count
- Paragraph Count

No buttons required — analysis happens automatically.

---

### 🔄 Character Counting Control

- Toggle whether **spaces are included** in character counts
- Useful for platforms with different submission rules

---

### 📋 Productivity Utilities

- Paste text directly from clipboard
- Clear workspace instantly
- Copy statistics with one click

Designed for quick workflows like assignments, documentation, and submissions.

---

### 🧱 Neo-Brutalist Interface

- Bold typography
- Hard shadows and structured layout
- Minimal distractions
- Focus on function over decoration

The interface treats writing as data — clear and measurable.

---

## 🛠️ Tech Stack

- Python 3
- Tkinter (GUI framework)
- Standard Library:
  - `re` (text parsing & pattern matching)

No external dependencies required.

---

## ⚙️ How It Works

1. The user types or pastes text into the editor.
2. Every key release triggers live analysis.
3. The application calculates:
   - Words using whitespace separation
   - Characters (with optional spaces)
   - Sentences using punctuation detection
   - Paragraphs using line breaks
4. Statistics update instantly in the analytics bar.

All processing happens locally in real time.

---

## ▶️ How to Run

1. Clone the repository:

```
git clone https://github.com/VipranshOjha/Daily-Problem-Solvers.git
```

2. Navigate to the project folder:
```
cd Daily-Problem-Solvers/Word-Counter
```
3. Run the application:
```
python main.py
```
