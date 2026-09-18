import math
from pathlib import Path
from tkinter import *

# ---------------------------- CONSTANTS ------------------------------- #
# Modern, refined color palette
BG_COLOR = "#1a1a2e"          # Deep navy background
CARD_BG = "#16213e"           # Slightly lighter card
ACCENT_GREEN = "#00d9a5"      # Vibrant mint for work
ACCENT_PINK = "#ff6b9d"       # Soft pink for short break
ACCENT_RED = "#ff4757"        # Strong red for long break
TEXT_PRIMARY = "#eaeaea"      # Off-white text
TEXT_SECONDARY = "#a0a0b8"    # Muted secondary text
BUTTON_BG = "#0f3460"         # Button base
BUTTON_HOVER = "#1a4a7a"
FONT_NAME = "Segoe UI"        # Clean modern system font (falls back gracefully)
FALLBACK_FONT = "Arial"

WORK_MIN = 25
SHORT_BREAK_MIN = 5
LONG_BREAK_MIN = 20

# ---------------------------- GLOBAL STATE ------------------------------- #
reps = 0
timer = None
is_running = False


# ---------------------------- HELPER ------------------------------- #
def get_font(size, weight="normal"):
    """Try modern font, fall back to Arial."""
    try:
        return (FONT_NAME, size, weight)
    except Exception:
        return (FALLBACK_FONT, size, weight)


# ---------------------------- TIMER RESET ------------------------------- #
def reset_timer():
    global reps, timer, is_running

    if timer is not None:
        window.after_cancel(timer)
        timer = None

    is_running = False
    reps = 0

    canvas.itemconfig(timer_text, text="25:00")
    headline.config(text="Pomodoro", fg=TEXT_PRIMARY)
    status_label.config(text="Ready to focus", fg=TEXT_SECONDARY)
    check_marks.config(text="")
    session_label.config(text="Session 0 / 4")

    start_button.config(state=NORMAL)
    reset_button.config(state=DISABLED)


# ---------------------------- TIMER MECHANISM ------------------------------- #
def start_timer():
    global reps, is_running

    if is_running:
        return

    is_running = True
    start_button.config(state=DISABLED)
    reset_button.config(state=NORMAL)

    reps += 1

    work_sec = WORK_MIN * 60
    short_break_sec = SHORT_BREAK_MIN * 60
    long_break_sec = LONG_BREAK_MIN * 60

    if reps % 8 == 0:
        count_down(long_break_sec)
        headline.config(text="Long Break", fg=ACCENT_RED)
        status_label.config(text="Take a well-deserved rest", fg=ACCENT_RED)
        session_label.config(text="Long Break")
    elif reps % 2 == 0:
        count_down(short_break_sec)
        headline.config(text="Short Break", fg=ACCENT_PINK)
        status_label.config(text="Stretch & breathe", fg=ACCENT_PINK)
        session_label.config(text=f"Break after session {reps // 2}")
    else:
        count_down(work_sec)
        headline.config(text="Focus Time", fg=ACCENT_GREEN)
        status_label.config(text="Deep work in progress", fg=ACCENT_GREEN)
        session_label.config(text=f"Session {(reps + 1) // 2} / 4")


# ---------------------------- COUNTDOWN MECHANISM ------------------------------- #
def count_down(count):
    global timer, is_running

    minutes = math.floor(count / 60)
    seconds = count % 60
    time_str = f"{minutes:02d}:{seconds:02d}"

    canvas.itemconfig(timer_text, text=time_str)

    if count > 0:
        timer = window.after(1000, count_down, count - 1)
    else:
        is_running = False
        # Update check marks after a completed work session
        work_sessions = math.floor(reps / 2)
        marks = "✓ " * work_sessions
        check_marks.config(text=marks.strip())

        # Auto-start next session
        start_timer()


# ---------------------------- UI SETUP ------------------------------- #
script_dir = Path(__file__).parent.resolve()
tomato_path = script_dir / "tomato.png"

window = Tk()
window.title("Pomodoro Timer")
window.config(bg=BG_COLOR, padx=40, pady=30)
window.resizable(False, False)

# Try to set a nice window icon (optional, fails silently if no icon)
try:
    window.iconphoto(False, PhotoImage(file=str(tomato_path)))
except Exception:
    pass

# ---- Header ----
headline = Label(
    window,
    text="Pomodoro",
    fg=TEXT_PRIMARY,
    bg=BG_COLOR,
    font=get_font(36, "bold"),
)
headline.grid(row=0, column=0, columnspan=3, pady=(0, 4))

status_label = Label(
    window,
    text="Ready to focus",
    fg=TEXT_SECONDARY,
    bg=BG_COLOR,
    font=get_font(12),
)
status_label.grid(row=1, column=0, columnspan=3, pady=(0, 18))

# ---- Canvas with tomato ----
canvas = Canvas(
    window,
    width=220,
    height=240,
    bg=BG_COLOR,
    highlightthickness=0,
)
tomato_img = PhotoImage(file=str(tomato_path))
canvas.create_image(110, 112, image=tomato_img)
timer_text = canvas.create_text(
    110, 130,
    text="25:00",
    fill="white",
    font=get_font(42, "bold"),
)
canvas.grid(row=2, column=0, columnspan=3, pady=(0, 12))

# ---- Session indicator ----
session_label = Label(
    window,
    text="Session 0 / 4",
    fg=TEXT_SECONDARY,
    bg=BG_COLOR,
    font=get_font(11),
)
session_label.grid(row=3, column=0, columnspan=3, pady=(0, 6))

# ---- Check marks ----
check_marks = Label(
    window,
    text="",
    fg=ACCENT_GREEN,
    bg=BG_COLOR,
    font=get_font(16),
)
check_marks.grid(row=4, column=0, columnspan=3, pady=(0, 20))

# ---- Buttons ----
button_style = {
    "font": get_font(12, "bold"),
    "width": 12,
    "height": 1,
    "bd": 0,
    "relief": "flat",
    "cursor": "hand2",
    "activeforeground": "white",
}

start_button = Button(
    window,
    text="START",
    bg=ACCENT_GREEN,
    fg="#0a0a0a",
    activebackground="#00b894",
    command=start_timer,
    **button_style,
)
start_button.grid(row=5, column=0, padx=10, pady=8)

reset_button = Button(
    window,
    text="RESET",
    bg=BUTTON_BG,
    fg=TEXT_PRIMARY,
    activebackground=BUTTON_HOVER,
    command=reset_timer,
    state=DISABLED,
    **button_style,
)
reset_button.grid(row=5, column=2, padx=10, pady=8)

# Center the middle column for balance
window.grid_columnconfigure(1, weight=1)

# ---- Footer hint ----
footer = Label(
    window,
    text="25 min focus  •  5 min break  •  20 min long break",
    fg="#5a5a78",
    bg=BG_COLOR,
    font=get_font(9),
)
footer.grid(row=6, column=0, columnspan=3, pady=(18, 0))

window.mainloop()
