import math
import platform
import subprocess
import sys
from pathlib import Path
from tkinter import *


def resource_path(relative_path: str) -> Path:
    """Get absolute path to resource — works in development and in PyInstaller .exe"""
    if hasattr(sys, "_MEIPASS"):
        # Running as a compiled executable
        return Path(sys._MEIPASS) / relative_path
    # Running as normal .py script
    return Path(__file__).parent.resolve() / relative_path


# ---------------------------- THEMES ------------------------------- #
THEMES = {
    "dark": {
        "bg": "#1a1a2e",
        "card": "#16213e",
        "green": "#00d9a5",
        "pink": "#ff6b9d",
        "red": "#ff4757",
        "text": "#eaeaea",
        "text_sec": "#a0a0b8",
        "btn": "#0f3460",
        "btn_hover": "#1a4a7a",
        "footer": "#5a5a78",
        "start_fg": "#0a0a0a",
    },
    "light": {
        "bg": "#f7f5dd",          # soft cream (classic pomodoro feel)
        "card": "#ffffff",
        "green": "#2ecc71",
        "pink": "#e84393",
        "red": "#e74c3c",
        "text": "#2d3436",
        "text_sec": "#636e72",
        "btn": "#dfe6e9",
        "btn_hover": "#b2bec3",
        "footer": "#b2bec3",
        "start_fg": "#ffffff",
    },
}

current_theme = "dark"
colors = THEMES[current_theme]

# ---------------------------- CONSTANTS ------------------------------- #
FONT_NAME = "Segoe UI"
FALLBACK_FONT = "Arial"

WORK_MIN = 25
SHORT_BREAK_MIN = 5
LONG_BREAK_MIN = 20

# ---------------------------- GLOBAL STATE ------------------------------- #
reps = 0
timer = None
is_running = False
is_paused = False
remaining_seconds = 0          # used for pause/resume


# ---------------------------- HELPERS ------------------------------- #
def get_font(size, weight="normal"):
    try:
        return (FONT_NAME, size, weight)
    except Exception:
        return (FALLBACK_FONT, size, weight)


def play_notification():
    """Cross-platform sound notification (no extra dependencies)."""
    system = platform.system()
    try:
        if system == "Windows":
            import winsound
            winsound.MessageBeep(winsound.MB_ICONASTERISK)
            # Slightly longer attention sound
            winsound.Beep(880, 300)
            winsound.Beep(1175, 300)
        elif system == "Darwin":  # macOS
            subprocess.call(
                ["afplay", "/System/Library/Sounds/Glass.aiff"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        else:  # Linux and others
            # Try common free-desktop sounds, fall back to terminal bell
            for sound in [
                "/usr/share/sounds/freedesktop/stereo/complete.oga",
                "/usr/share/sounds/freedesktop/stereo/bell.oga",
                "/usr/share/sounds/ubuntu/stereo/message.ogg",
            ]:
                if Path(sound).exists():
                    subprocess.call(
                        ["paplay", sound],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                    return
            print("\a", end="", flush=True)  # terminal bell fallback
    except Exception:
        print("\a", end="", flush=True)


def apply_theme():
    """Re-color the entire UI according to current_theme."""
    global colors
    colors = THEMES[current_theme]

    window.config(bg=colors["bg"])
    headline.config(bg=colors["bg"], fg=colors["text"])
    status_label.config(bg=colors["bg"], fg=colors["text_sec"])
    session_label.config(bg=colors["bg"], fg=colors["text_sec"])
    check_marks.config(bg=colors["bg"], fg=colors["green"])
    footer.config(bg=colors["bg"], fg=colors["footer"])
    canvas.config(bg=colors["bg"])

    # Buttons
    start_pause_btn.config(
        bg=colors["green"],
        fg=colors["start_fg"],
        activebackground=colors["green"],
        activeforeground=colors["start_fg"],
    )
    reset_button.config(
        bg=colors["btn"],
        fg=colors["text"],
        activebackground=colors["btn_hover"],
        activeforeground=colors["text"],
    )
    theme_button.config(
        bg=colors["btn"],
        fg=colors["text"],
        activebackground=colors["btn_hover"],
        activeforeground=colors["text"],
    )

    # Keep phase colors correct if a session is active
    if not is_running and not is_paused:
        headline.config(fg=colors["text"])
        status_label.config(fg=colors["text_sec"])


def toggle_theme():
    global current_theme
    current_theme = "light" if current_theme == "dark" else "dark"
    theme_button.config(text="🌙 Dark" if current_theme == "light" else "☀️ Light")
    apply_theme()


# ---------------------------- TIMER RESET ------------------------------- #
def reset_timer():
    global reps, timer, is_running, is_paused, remaining_seconds

    if timer is not None:
        window.after_cancel(timer)
        timer = None

    is_running = False
    is_paused = False
    remaining_seconds = 0
    reps = 0

    canvas.itemconfig(timer_text, text="25:00")
    headline.config(text="Pomodoro", fg=colors["text"])
    status_label.config(text="Ready to focus", fg=colors["text_sec"])
    check_marks.config(text="")
    session_label.config(text="Session 0 / 4")

    start_pause_btn.config(text="START", state=NORMAL)
    reset_button.config(state=DISABLED)


# ---------------------------- TIMER MECHANISM ------------------------------- #
def start_or_pause():
    """Single button that acts as Start / Pause / Resume."""
    global is_running, is_paused, remaining_seconds, timer

    if not is_running and not is_paused:
        # Fresh start
        start_new_session()
    elif is_running and not is_paused:
        # Pause
        if timer is not None:
            window.after_cancel(timer)
            timer = None
        is_running = False
        is_paused = True
        start_pause_btn.config(text="RESUME")
        status_label.config(text="Paused", fg=colors["text_sec"])
    elif is_paused:
        # Resume
        is_running = True
        is_paused = False
        start_pause_btn.config(text="PAUSE")
        # Restore phase label color
        if reps % 8 == 0:
            status_label.config(text="Take a well-deserved rest", fg=colors["red"])
        elif reps % 2 == 0:
            status_label.config(text="Stretch & breathe", fg=colors["pink"])
        else:
            status_label.config(text="Deep work in progress", fg=colors["green"])
        count_down(remaining_seconds)


def start_new_session():
    global reps, is_running, is_paused

    is_running = True
    is_paused = False
    start_pause_btn.config(text="PAUSE")
    reset_button.config(state=NORMAL)

    reps += 1

    work_sec = WORK_MIN * 60
    short_break_sec = SHORT_BREAK_MIN * 60
    long_break_sec = LONG_BREAK_MIN * 60

    if reps % 8 == 0:
        headline.config(text="Long Break", fg=colors["red"])
        status_label.config(text="Take a well-deserved rest", fg=colors["red"])
        session_label.config(text="Long Break")
        count_down(long_break_sec)
    elif reps % 2 == 0:
        headline.config(text="Short Break", fg=colors["pink"])
        status_label.config(text="Stretch & breathe", fg=colors["pink"])
        session_label.config(text=f"Break after session {reps // 2}")
        count_down(short_break_sec)
    else:
        headline.config(text="Focus Time", fg=colors["green"])
        status_label.config(text="Deep work in progress", fg=colors["green"])
        session_label.config(text=f"Session {(reps + 1) // 2} / 4")
        count_down(work_sec)


# ---------------------------- COUNTDOWN MECHANISM ------------------------------- #
def count_down(count):
    global timer, is_running, remaining_seconds

    remaining_seconds = count
    minutes = math.floor(count / 60)
    seconds = count % 60
    canvas.itemconfig(timer_text, text=f"{minutes:02d}:{seconds:02d}")

    if count > 0:
        timer = window.after(1000, count_down, count - 1)
    else:
        # Session finished
        is_running = False
        play_notification()

        work_sessions = math.floor(reps / 2)
        marks = "✓ " * work_sessions
        check_marks.config(text=marks.strip())

        # Automatically start next phase
        start_new_session()


# ---------------------------- UI SETUP ------------------------------- #
tomato_path = resource_path("tomato.png")


window = Tk()
window.title("Pomodoro Timer")
window.config(bg=colors["bg"], padx=40, pady=30)
window.resizable(False, False)

try:
    window.iconphoto(False, PhotoImage(file=str(tomato_path)))
except Exception:
    pass

# ---- Header ----
headline = Label(
    window, text="Pomodoro", fg=colors["text"], bg=colors["bg"],
    font=get_font(36, "bold")
)
headline.grid(row=0, column=0, columnspan=3, pady=(0, 4))

status_label = Label(
    window, text="Ready to focus", fg=colors["text_sec"], bg=colors["bg"],
    font=get_font(12)
)
status_label.grid(row=1, column=0, columnspan=3, pady=(0, 18))

# ---- Canvas ----
canvas = Canvas(window, width=220, height=240, bg=colors["bg"], highlightthickness=0)
tomato_img = PhotoImage(file=str(tomato_path))
canvas.create_image(110, 112, image=tomato_img)
timer_text = canvas.create_text(
    110, 130, text="25:00", fill="white", font=get_font(42, "bold")
)
canvas.grid(row=2, column=0, columnspan=3, pady=(0, 12))

# ---- Session + checks ----
session_label = Label(
    window, text="Session 0 / 4", fg=colors["text_sec"], bg=colors["bg"],
    font=get_font(11)
)
session_label.grid(row=3, column=0, columnspan=3, pady=(0, 6))

check_marks = Label(
    window, text="", fg=colors["green"], bg=colors["bg"], font=get_font(16)
)
check_marks.grid(row=4, column=0, columnspan=3, pady=(0, 20))

# ---- Buttons ----
btn_style = {
    "font": get_font(11, "bold"),
    "width": 11,
    "height": 1,
    "bd": 0,
    "relief": "flat",
    "cursor": "hand2",
}

start_pause_btn = Button(
    window,
    text="START",
    bg=colors["green"],
    fg=colors["start_fg"],
    activebackground=colors["green"],
    activeforeground=colors["start_fg"],
    command=start_or_pause,
    **btn_style,
)
start_pause_btn.grid(row=5, column=0, padx=6, pady=8)

reset_button = Button(
    window,
    text="RESET",
    bg=colors["btn"],
    fg=colors["text"],
    activebackground=colors["btn_hover"],
    activeforeground=colors["text"],
    command=reset_timer,
    state=DISABLED,
    **btn_style,
)
reset_button.grid(row=5, column=1, padx=6, pady=8)

theme_button = Button(
    window,
    text="☀️ Light",
    bg=colors["btn"],
    fg=colors["text"],
    activebackground=colors["btn_hover"],
    activeforeground=colors["text"],
    command=toggle_theme,
    **btn_style,
)
theme_button.grid(row=5, column=2, padx=6, pady=8)

window.grid_columnconfigure(0, weight=1)
window.grid_columnconfigure(1, weight=1)
window.grid_columnconfigure(2, weight=1)

# ---- Footer ----
footer = Label(
    window,
    text="25 min focus  •  5 min break  •  20 min long break",
    fg=colors["footer"],
    bg=colors["bg"],
    font=get_font(9),
)
footer.grid(row=6, column=0, columnspan=3, pady=(18, 0))

window.mainloop()
