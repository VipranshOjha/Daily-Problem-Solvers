import pygame
import sys
import time
import random

# INIT 
pygame.init()
WIDTH, HEIGHT = 1100, 750
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TYPING / SPEED / RAW")
CLOCK = pygame.time.Clock()

# COLORS 
ACCENT = (146, 119, 176)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (140, 140, 140)
PURPLE_TEXT = (107, 45, 255)

# FONTS 
FONT_TITLE = pygame.font.SysFont("arialblack", 36)
FONT_TEXT = pygame.font.SysFont("arialblack", 20)
FONT_MONO = pygame.font.SysFont("consolas", 24, bold=True)

# CONFIG 
BORDER = 4
SHADOW = 8
PROMPT_WIDTH = 720

BASE_SENTENCES = [
    "Neo brutalism values clarity over comfort",
    "Typing fast requires accuracy and discipline",
    "Raw interfaces expose real performance",
    "Consistency matters more than short bursts of speed",
    "Each keystroke reflects focus and intent",
    "Errors are information not failure",
    "Calm hands produce reliable output",
    "Speed emerges naturally from correctness",
    "Minimal interfaces reveal true skill",
]

# TEXT ENGINE 
def split_sentence(sentence):
    words = sentence.split(" ")
    lines, current = [], ""
    for w in words:
        test = current + (" " if current else "") + w
        if FONT_MONO.size(test)[0] <= PROMPT_WIDTH:
            current = test
        else:
            lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines

def build_sentence_queue():
    pool = BASE_SENTENCES.copy()
    random.shuffle(pool)
    queue = []
    for s in pool:
        queue.extend(split_sentence(s))
    return queue

# STATE 
def reset_test():
    global sentence_queue, sentence_index, text
    global typed, mistakes, correct_total, typed_total
    global start_time, running, finished, wpm_history, last_sample

    sentence_queue = build_sentence_queue()
    sentence_index = 0
    text = sentence_queue[sentence_index]

    typed = ""
    mistakes = set()

    correct_total = 0
    typed_total = 0

    start_time = None
    running = False
    finished = False

    wpm_history = []
    last_sample = 0

duration = 30
strict_mode = True
reset_test()

#  HELPERS 
def brutal_rect(rect, fill):
    pygame.draw.rect(SCREEN, BLACK, rect.move(SHADOW, SHADOW))
    pygame.draw.rect(SCREEN, fill, rect)
    pygame.draw.rect(SCREEN, BLACK, rect, BORDER)

def average_wpm():
    return sum(wpm_history) // len(wpm_history) if wpm_history else 0

def final_accuracy():
    if typed_total == 0:
        return 0
    return int((correct_total / typed_total) * 100)

# UI BUTTON 
class Button:
    def __init__(self, rect, label_fn, fill_fn, action):
        self.rect = pygame.Rect(rect)
        self.label_fn = label_fn
        self.fill_fn = fill_fn
        self.action = action

    def draw(self):
        pygame.draw.rect(SCREEN, BLACK, self.rect.move(SHADOW, SHADOW))
        pygame.draw.rect(SCREEN, self.fill_fn(), self.rect)
        pygame.draw.rect(SCREEN, BLACK, self.rect, BORDER)
        SCREEN.blit(
            FONT_TEXT.render(self.label_fn(), True, BLACK),
            (self.rect.x + 10, self.rect.y + 12)
        )

    def handle(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.action()

def toggle_strict():
    global strict_mode
    strict_mode = not strict_mode

def toggle_mode():
    global duration
    duration = 60 if duration == 30 else 30
    reset_test()

def restart():
    reset_test()

buttons = [
    Button((40,130,220,45),
        lambda: f"STRICT: {'ON' if strict_mode else 'OFF'}",
        lambda: ACCENT if strict_mode else WHITE,
        toggle_strict),
    Button((40,190,220,45),
        lambda: f"MODE: {duration}s",
        lambda: ACCENT,
        toggle_mode),
    Button((40,250,220,45),
        lambda: "RESTART",
        lambda: ACCENT,
        restart),
]

# DRAW PROMPT 
def draw_prompt(x, y):
    cx = x
    for i, ch in enumerate(text):
        if i < len(typed):
            if typed[i] == ch:
                color = PURPLE_TEXT
            else:
                color = BLACK
                pygame.draw.rect(SCREEN, ACCENT, (cx-2, y-2, 18, 30))
        else:
            color = GRAY
        surf = FONT_MONO.render(ch, True, color)
        SCREEN.blit(surf, (cx, y))
        cx += surf.get_width()

# GRAPH 
def draw_graph(rect):
    if len(wpm_history) < 2:
        return
    max_wpm = max(wpm_history) + 5
    step = rect.width / (len(wpm_history) - 1)
    points = [
        (rect.x + i * step,
         rect.bottom - (w / max_wpm) * rect.height)
        for i, w in enumerate(wpm_history)
    ]
    pygame.draw.lines(SCREEN, PURPLE_TEXT, False, points, 4)

# MAIN LOOP 
while True:
    CLOCK.tick(60)
    SCREEN.fill(WHITE)
    now = time.time()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        for b in buttons:
            b.handle(event)

        if event.type == pygame.KEYDOWN and not finished:
            if event.key == pygame.K_RETURN:
                finished = True
                running = False

            elif event.key == pygame.K_BACKSPACE and running:
                if typed:
                    typed = typed[:-1]
                    typed_total += 1

            elif running and event.unicode:
                typed += event.unicode
                typed_total += 1
                if len(typed) <= len(text) and typed[-1] == text[len(typed)-1]:
                    correct_total += 1

            elif not running:
                running = True
                start_time = now

    # Sentence advance
    if running and len(typed) >= len(text):
        typed = ""
        sentence_index += 1
        if sentence_index >= len(sentence_queue):
            sentence_queue = build_sentence_queue()
            sentence_index = 0
        text = sentence_queue[sentence_index]

    # Timing / WPM
    if running:
        elapsed = max(now - start_time, 1)
        wpm = int((correct_total / 5) / (elapsed / 60))
        if int(elapsed) != last_sample:
            wpm_history.append(wpm)
            last_sample = int(elapsed)
        if elapsed >= duration:
            running = False
            finished = True

    # UI 
    brutal_rect(pygame.Rect(300,30,500,70), ACCENT)
    SCREEN.blit(FONT_TITLE.render("TYPING SPEED TEST", True, BLACK), (330,45))

    if not finished:
        brutal_rect(pygame.Rect(300,130,760,90), WHITE)
        draw_prompt(320,160)

        brutal_rect(pygame.Rect(300,250,760,110), WHITE)
        SCREEN.blit(FONT_MONO.render(typed[-60:], True, BLACK), (320,290))
    else:
        brutal_rect(pygame.Rect(300,130,760,230), WHITE)
        SCREEN.blit(FONT_TITLE.render("RESULTS", True, BLACK), (540,160))
        SCREEN.blit(FONT_TEXT.render(f"Average WPM: {average_wpm()}", True, BLACK), (500,215))
        SCREEN.blit(FONT_TEXT.render(f"Accuracy: {final_accuracy()}%", True, BLACK), (500,245))
        SCREEN.blit(FONT_TEXT.render("Press RESTART to try again", True, BLACK), (470,290))

    brutal_rect(pygame.Rect(300,390,760,60), ACCENT)
    SCREEN.blit(
        FONT_TEXT.render(
            f"WPM: {average_wpm() if finished else (wpm if running else 0)}   ACC: {final_accuracy()}%   TIME: {duration}s",
            True, BLACK
        ),
        (320,408)
    )

    brutal_rect(pygame.Rect(300,480,760,180), WHITE)
    draw_graph(pygame.Rect(300,480,760,180))

    for b in buttons:
        b.draw()

    pygame.display.flip()
