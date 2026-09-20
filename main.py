import math
import platform
import subprocess
from pathlib import Path
from tkinter import *
from tkinter import messagebox, font as tkfont


# ───────────────────────────────────────────────
# COLORS
# ───────────────────────────────────────────────
colors = {
    "bg": "#0f0f13",
    "surface": "#1a1a24",
    "surface2": "#242433",
    "border": "#2e2e42",
    "accent": "#7c6cff",
    "accent_dim": "#5a4fcf",
    "work": "#4ade80",
    "short": "#f472b6",
    "long": "#fb7185",
    "text": "#f1f1f6",
    "text_sec": "#9b9bb0",
    "text_dim": "#6b6b80",
    "btn": "#2a2a3c",
    "btn_hover": "#363650",
    "input_bg": "#16161f",
    "start_fg": "#0f0f13",
}

settings = {
    "work_min": 25,
    "short_break_min": 5,
    "long_break_min": 20,
    "sessions_until_long": 4,
    "auto_start": True,
}

reps = 0
timer_id = None
is_running = False
is_paused = False
remaining_seconds = 0
current_phase = "idle"
work_sessions_done = 0

SCALE = 1.0

# Font families — picked once at startup from what the OS provides
FONT_UI = "Segoe UI"
FONT_DISPLAY = "Segoe UI"
FONT_TIMER = "Consolas"


def S(value):
    return max(1, int(round(value * SCALE)))


def get_font(size, weight="normal", family=None):
    fam = family or FONT_UI
    return (fam, max(8, S(size)), weight)


def _pick_fonts():
    """Choose the coolest available system fonts."""
    global FONT_UI, FONT_DISPLAY, FONT_TIMER
    available = {f.lower(): f for f in tkfont.families()}

    def pick(*candidates, fallback="Arial"):
        for c in candidates:
            if c.lower() in available:
                return available[c.lower()]
        return fallback

    # UI body text
    FONT_UI = pick(
        "Segoe UI", "SF Pro Text", "Helvetica Neue", "Inter",
        "Ubuntu", "Cantarell", "Arial",
    )
    # Titles / headings
    FONT_DISPLAY = pick(
        "Segoe UI Semibold", "Segoe UI", "SF Pro Display",
        "Helvetica Neue", "Trebuchet MS", "Arial",
    )
    # Digital timer — monospace looks sharp
    FONT_TIMER = pick(
        "Cascadia Code", "Cascadia Mono", "JetBrains Mono",
        "Consolas", "SF Mono", "Menlo", "Courier New", "Courier",
    )


# ───────────────────────────────────────────────
# ROUNDED BUTTON (Canvas-based, CSS-like radius)
# ───────────────────────────────────────────────
class RoundedButton(Canvas):
    def __init__(
        self,
        parent,
        text,
        command=None,
        bg=None,
        fg=None,
        hover_bg=None,
        radius=12,
        padx=18,
        pady=10,
        font=None,
        state=NORMAL,
        **kwargs,
    ):
        self._command = command
        self._text = text
        self._bg = bg or colors["btn"]
        self._fg = fg or colors["text"]
        self._hover_bg = hover_bg or colors["btn_hover"]
        self._radius = S(radius)
        self._padx = S(padx)
        self._pady = S(pady)
        self._font = font or get_font(11, "bold")
        self._state = state
        self._enabled = state == NORMAL

        super().__init__(
            parent,
            highlightthickness=0,
            bd=0,
            bg=parent.cget("bg") if parent else colors["bg"],
            **kwargs,
        )

        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self._draw()

    def _measure(self):
        # Temporary text to measure
        tid = self.create_text(0, 0, text=self._text, font=self._font, anchor="nw")
        bbox = self.bbox(tid)
        self.delete(tid)
        if bbox:
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
        else:
            tw, th = 60, 16
        return tw + self._padx * 2, th + self._pady * 2

    def _draw(self, fill=None):
        self.delete("all")
        w, h = self._measure()
        self.configure(width=w, height=h)
        fill = fill or self._bg
        r = min(self._radius, h // 2, w // 2)

        # Rounded rectangle via polygon + smooth
        self.create_polygon(
            self._rounded_points(0, 0, w, h, r),
            fill=fill,
            outline="",
            smooth=True,
        )
        text_color = self._fg if self._enabled else colors["text_dim"]
        self.create_text(
            w // 2,
            h // 2,
            text=self._text,
            fill=text_color,
            font=self._font,
        )

    @staticmethod
    def _rounded_points(x1, y1, x2, y2, r):
        """Approximate rounded rect as a smooth polygon."""
        return [
            x1 + r, y1,
            x2 - r, y1,
            x2, y1,
            x2, y1 + r,
            x2, y2 - r,
            x2, y2,
            x2 - r, y2,
            x1 + r, y2,
            x1, y2,
            x1, y2 - r,
            x1, y1 + r,
            x1, y1,
        ]

    def _on_click(self, _event=None):
        if self._enabled and self._command:
            self._command()

    def _on_enter(self, _event=None):
        if self._enabled:
            self._draw(fill=self._hover_bg)
            self.configure(cursor="hand2")

    def _on_leave(self, _event=None):
        self._draw()
        self.configure(cursor="")

    def configure(self, **kwargs):
        # Support text / state / command updates like a normal Button
        redraw = False
        if "text" in kwargs:
            self._text = kwargs.pop("text")
            redraw = True
        if "state" in kwargs:
            st = kwargs.pop("state")
            self._state = st
            self._enabled = st == NORMAL
            redraw = True
        if "command" in kwargs:
            self._command = kwargs.pop("command")
        if "bg" in kwargs:
            self._bg = kwargs.pop("bg")
            redraw = True
        if "fg" in kwargs:
            self._fg = kwargs.pop("fg")
            redraw = True
        if kwargs:
            super().configure(**kwargs)
        if redraw:
            self._draw()

    config = configure


# ───────────────────────────────────────────────
# NOTIFICATIONS
# ───────────────────────────────────────────────
def play_notification():
    system = platform.system()
    try:
        if system == "Windows":
            import winsound
            winsound.MessageBeep(winsound.MB_ICONASTERISK)
            winsound.Beep(880, 280)
            winsound.Beep(1175, 320)
        elif system == "Darwin":
            subprocess.call(
                ["afplay", "/System/Library/Sounds/Glass.aiff"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        else:
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
            print("\a", end="", flush=True)
    except Exception:
        print("\a", end="", flush=True)


def show_priority_popup(title: str, message: str, phase_color: str):
    popup = Toplevel(window)
    popup.title(title)
    popup.configure(bg=colors["surface"])
    popup.resizable(False, False)
    popup.attributes("-topmost", True)
    popup.lift()
    popup.focus_force()
    try:
        if platform.system() == "Windows":
            popup.wm_attributes("-topmost", 1)
    except Exception:
        pass

    w, h = S(380), S(220)
    sw = popup.winfo_screenwidth()
    sh = popup.winfo_screenheight()
    popup.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 3}")

    Frame(popup, bg=phase_color, height=S(6)).pack(fill=X)
    Label(
        popup, text=title, font=get_font(18, "bold", FONT_DISPLAY),
        fg=colors["text"], bg=colors["surface"],
    ).pack(pady=(S(18), S(6)))
    Label(
        popup, text=message, font=get_font(12),
        fg=colors["text_sec"], bg=colors["surface"],
        justify=CENTER, wraplength=S(340),
    ).pack(pady=(0, S(16)))

    def close_and_focus():
        popup.destroy()
        window.lift()
        window.focus_force()

    RoundedButton(
        popup,
        text="Got it",
        command=close_and_focus,
        bg=phase_color,
        fg="#0f0f13",
        hover_bg=phase_color,
        radius=10,
        padx=24,
        pady=8,
    ).pack(pady=(0, S(16)))

    popup.after(12000, lambda: popup.destroy() if popup.winfo_exists() else None)


# ───────────────────────────────────────────────
# SETTINGS / FOOTER / WINDOW FIT
# ───────────────────────────────────────────────
def apply_settings_from_ui():
    try:
        settings["work_min"] = max(1, int(work_spin.get()))
        settings["short_break_min"] = max(1, int(short_spin.get()))
        settings["long_break_min"] = max(1, int(long_spin.get()))
        settings["sessions_until_long"] = max(1, int(sessions_spin.get()))
        settings["auto_start"] = auto_var.get()
    except ValueError:
        messagebox.showerror("Invalid input", "Please enter positive whole numbers.")
        return False
    return True


def update_footer():
    footer.configure(
        text=(
            f"{settings['work_min']} min focus  ·  "
            f"{settings['short_break_min']} min short break  ·  "
            f"{settings['long_break_min']} min long break  ·  "
            f"{settings['sessions_until_long']} sessions → long break"
        )
    )


def fit_window_to_content():
    window.update_idletasks()
    req_h = root_frame.winfo_reqheight() + S(32)
    req_w = max(window.winfo_width(), S(400))
    x, y = window.winfo_x(), window.winfo_y()
    max_h = int(window.winfo_screenheight() * 0.92)
    window.geometry(f"{req_w}x{min(req_h, max_h)}+{x}+{y}")


def lock_settings(locked: bool):
    """Hide settings while running; show again when idle. Window height adjusts."""
    if locked:
        settings_card.pack_forget()
        # Footer stays — shows the locked-in timer config
        footer.pack(pady=(S(14), S(2)))
    else:
        settings_card.pack(fill=X, pady=(S(8), 0), before=footer)
        footer.pack(pady=(S(14), S(2)))
    fit_window_to_content()


# ───────────────────────────────────────────────
# TIMER LOGIC
# ───────────────────────────────────────────────
def format_time(secs: int) -> str:
    return f"{math.floor(secs / 60):02d}:{secs % 60:02d}"


def reset_timer():
    global reps, timer_id, is_running, is_paused, remaining_seconds
    global current_phase, work_sessions_done

    if timer_id is not None:
        window.after_cancel(timer_id)
        timer_id = None

    is_running = False
    is_paused = False
    remaining_seconds = 0
    reps = 0
    work_sessions_done = 0
    current_phase = "idle"

    time_lbl.configure(text=format_time(settings["work_min"] * 60), fg=colors["text"])
    phase_lbl.configure(text="Ready", fg=colors["text_sec"])
    session_info.configure(text="Press Start when you're ready")
    start_btn.configure(text="▶  Start")
    reset_btn.configure(state=DISABLED)
    skip_btn.configure(state=DISABLED)
    lock_settings(False)
    _update_session_dots()
    update_footer()


def start_or_pause():
    global is_running, is_paused, remaining_seconds, timer_id

    if not is_running and not is_paused:
        if not apply_settings_from_ui():
            return
        update_footer()
        lock_settings(True)
        start_new_phase()
    elif is_running and not is_paused:
        if timer_id is not None:
            window.after_cancel(timer_id)
            timer_id = None
        is_running = False
        is_paused = True
        start_btn.configure(text="▶  Resume")
        phase_lbl.configure(text="Paused")
        session_info.configure(text="Timer paused — resume when ready")
    elif is_paused:
        is_running = True
        is_paused = False
        start_btn.configure(text="⏸  Pause")
        _set_phase_labels()
        count_down(remaining_seconds)


def skip_phase():
    global timer_id, is_running, is_paused
    if timer_id is not None:
        window.after_cancel(timer_id)
        timer_id = None
    is_running = False
    is_paused = False
    on_phase_complete(skipped=True)


def start_new_phase():
    global reps, is_running, is_paused, current_phase

    is_running = True
    is_paused = False
    start_btn.configure(text="⏸  Pause")
    reset_btn.configure(state=NORMAL)
    skip_btn.configure(state=NORMAL)

    reps += 1
    sessions = settings["sessions_until_long"]

    if reps % 2 == 1:
        current_phase = "work"
        secs = settings["work_min"] * 60
    else:
        completed_works = reps // 2
        if completed_works % sessions == 0:
            current_phase = "long"
            secs = settings["long_break_min"] * 60
        else:
            current_phase = "short"
            secs = settings["short_break_min"] * 60

    _set_phase_labels()
    count_down(secs)


def _set_phase_labels():
    sessions = settings["sessions_until_long"]
    if current_phase == "work":
        phase_lbl.configure(text="Focus", fg=colors["work"])
        time_lbl.configure(fg=colors["work"])
        session_info.configure(
            text=f"Session {work_sessions_done + 1} of {sessions}  ·  Deep work"
        )
    elif current_phase == "short":
        phase_lbl.configure(text="Short Break", fg=colors["short"])
        time_lbl.configure(fg=colors["short"])
        session_info.configure(text="Stretch, hydrate, look away from the screen")
    elif current_phase == "long":
        phase_lbl.configure(text="Long Break", fg=colors["long"])
        time_lbl.configure(fg=colors["long"])
        session_info.configure(text="Well done — take a real rest")
    _update_session_dots()


def count_down(count: int):
    global timer_id, is_running, remaining_seconds
    remaining_seconds = count
    time_lbl.configure(text=format_time(count))
    if count > 0:
        timer_id = window.after(1000, count_down, count - 1)
    else:
        is_running = False
        on_phase_complete(skipped=False)


def on_phase_complete(skipped: bool = False):
    global work_sessions_done, current_phase

    if current_phase == "work" and not skipped:
        work_sessions_done += 1

    play_notification()

    if current_phase == "work":
        title = "Focus session complete"
        msg = f"Session {work_sessions_done} finished.\nNext: {_preview_next()}"
        color = colors["work"]
    elif current_phase == "short":
        title = "Short break over"
        msg = f"Back to work.\nNext: {_preview_next()}"
        color = colors["short"]
    else:
        title = "Long break finished"
        msg = f"Ready for a new cycle.\nNext: {_preview_next()}"
        color = colors["long"]

    show_priority_popup(title, msg, color)
    _update_session_dots()

    if settings["auto_start"]:
        start_new_phase()
    else:
        current_phase = "idle"
        phase_lbl.configure(text="Ready for next", fg=colors["text_sec"])
        time_lbl.configure(text="— — : — —", fg=colors["text"])
        session_info.configure(text="Click Start to begin the next phase")
        start_btn.configure(text="▶  Start next")
        skip_btn.configure(state=DISABLED)


def _preview_next() -> str:
    sessions = settings["sessions_until_long"]
    next_reps = reps + 1
    if next_reps % 2 == 1:
        return f"Focus ({settings['work_min']} min)"
    completed = next_reps // 2
    if completed % sessions == 0:
        return f"Long break ({settings['long_break_min']} min)"
    return f"Short break ({settings['short_break_min']} min)"


def _update_session_dots():
    for w in dots_frame.winfo_children():
        w.destroy()
    sessions = settings["sessions_until_long"]
    dot_size = S(12)
    for i in range(sessions):
        filled = i < work_sessions_done
        active = (i == work_sessions_done) and current_phase == "work"
        if filled:
            c = colors["work"]
        elif active:
            c = colors["accent"]
        else:
            c = colors["border"]
        dot = Canvas(
            dots_frame, width=dot_size, height=dot_size,
            bg=colors["surface"], highlightthickness=0,
        )
        pad = max(1, S(1))
        dot.create_oval(pad, pad, dot_size - pad, dot_size - pad, fill=c, outline="")
        dot.pack(side=LEFT, padx=S(3))


# ───────────────────────────────────────────────
# UI
# ───────────────────────────────────────────────
window = Tk()
window.title("Pomodoro")
window.configure(bg=colors["bg"])
_pick_fonts()

screen_w = window.winfo_screenwidth()
screen_h = window.winfo_screenheight()
SCALE = max(0.65, min(1.35, min(screen_w * 0.92 / 420, screen_h * 0.88 / 640)))

win_w = S(420)
win_h = S(560)
pos_x = max(0, (screen_w - win_w) // 2)
pos_y = max(0, (screen_h - win_h) // 4)
window.geometry(f"{win_w}x{win_h}+{pos_x}+{pos_y}")
window.minsize(S(340), S(360))
window.resizable(False, False)

root_frame = Frame(window, bg=colors["bg"])
root_frame.pack(fill=BOTH, expand=True, padx=S(20), pady=S(14))

# ── Header (centered) ──
title_lbl = Label(
    root_frame,
    text="Pomodoro",
    font=get_font(28, "bold", FONT_DISPLAY),
    fg=colors["text"],
    bg=colors["bg"],
)
title_lbl.pack(pady=(S(4), S(2)))

subtitle_lbl = Label(
    root_frame,
    text="Focus · Break · Repeat",
    font=get_font(12, family=FONT_UI),
    fg=colors["text_sec"],
    bg=colors["bg"],
)
subtitle_lbl.pack(pady=(0, S(14)))

# ── Timer card ──
main_card = Frame(
    root_frame,
    bg=colors["surface"],
    highlightbackground=colors["border"],
    highlightthickness=1,
    padx=S(20),
    pady=S(18),
)
main_card.pack(fill=X)

timer_frame = Frame(main_card, bg=colors["surface"])
timer_frame.pack()

phase_lbl = Label(
    timer_frame,
    text="Ready",
    font=get_font(13, "bold", FONT_DISPLAY),
    fg=colors["text_sec"],
    bg=colors["surface"],
)
phase_lbl.pack(pady=(0, S(4)))

time_lbl = Label(
    timer_frame,
    text="25:00",
    font=get_font(52, "bold", FONT_TIMER),
    fg=colors["text"],
    bg=colors["surface"],
)
time_lbl.pack()

session_info = Label(
    timer_frame,
    text="Press Start when you're ready",
    font=get_font(11),
    fg=colors["text_sec"],
    bg=colors["surface"],
    wraplength=S(300),
    justify=CENTER,
)
session_info.pack(pady=(S(8), S(10)))

dots_frame = Frame(timer_frame, bg=colors["surface"])
dots_frame.pack(pady=(0, S(2)))
_update_session_dots()

# ── Buttons (rounded) ──
controls_frame = Frame(root_frame, bg=colors["bg"])
controls_frame.pack(pady=S(14))

start_btn = RoundedButton(
    controls_frame,
    text="▶  Start",
    command=start_or_pause,
    bg=colors["accent"],
    fg=colors["start_fg"],
    hover_bg=colors["accent_dim"],
    radius=14,
    padx=18,
    pady=10,
    font=get_font(11, "bold", FONT_UI),
)
start_btn.pack(side=LEFT, padx=S(5))

reset_btn = RoundedButton(
    controls_frame,
    text="Reset",
    command=reset_timer,
    bg=colors["btn"],
    fg=colors["text"],
    hover_bg=colors["btn_hover"],
    radius=14,
    padx=18,
    pady=10,
    font=get_font(11, "bold", FONT_UI),
    state=DISABLED,
)
reset_btn.pack(side=LEFT, padx=S(5))

skip_btn = RoundedButton(
    controls_frame,
    text="Skip",
    command=skip_phase,
    bg=colors["btn"],
    fg=colors["text"],
    hover_bg=colors["btn_hover"],
    radius=14,
    padx=18,
    pady=10,
    font=get_font(11, "bold", FONT_UI),
    state=DISABLED,
)
skip_btn.pack(side=LEFT, padx=S(5))

# ── Settings ──
settings_card = Frame(
    root_frame,
    bg=colors["surface"],
    highlightbackground=colors["border"],
    highlightthickness=1,
    padx=S(16),
    pady=S(12),
)
settings_card.pack(fill=X, pady=(S(4), 0))

settings_title = Label(
    settings_card,
    text="Settings  (edit before starting)",
    font=get_font(12, "bold", FONT_DISPLAY),
    fg=colors["text"],
    bg=colors["surface"],
)
settings_title.pack(anchor=W, pady=(0, S(8)))

settings_inner = Frame(settings_card, bg=colors["surface"])
settings_inner.pack(fill=X)


def make_setting_row(parent, label_text, default, from_=1, to=120):
    row = Frame(parent, bg=colors["surface"])
    row.pack(fill=X, pady=S(3))
    Label(
        row,
        text=label_text,
        font=get_font(11),
        fg=colors["text_sec"],
        bg=colors["surface"],
        anchor=W,
        bd=0,
        highlightthickness=0,
        relief=FLAT,
    ).pack(side=LEFT, fill=X, expand=True)

    border = Frame(row, bg=colors["border"], padx=1, pady=1)
    border.pack(side=RIGHT)
    spin = Spinbox(
        border,
        from_=from_,
        to=to,
        width=6,
        font=get_font(11),
        bg=colors["input_bg"],
        fg=colors["text"],
        buttonbackground=colors["btn"],
        highlightthickness=0,
        bd=0,
        relief=FLAT,
        justify=CENTER,
        insertbackground=colors["text"],
    )
    spin.delete(0, END)
    spin.insert(0, str(default))
    spin.pack()
    return spin


work_spin = make_setting_row(settings_inner, "Work (minutes)", 25)
short_spin = make_setting_row(settings_inner, "Short break (min)", 5)
long_spin = make_setting_row(settings_inner, "Long break (min)", 20)
sessions_spin = make_setting_row(
    settings_inner, "Sessions → long break", 4, from_=1, to=12
)

auto_row = Frame(settings_inner, bg=colors["surface"])
auto_row.pack(fill=X, pady=(S(8), S(2)))

auto_var = BooleanVar(value=True)
auto_check = Checkbutton(
    auto_row,
    text="Auto-start next phase when timer ends",
    variable=auto_var,
    font=get_font(11),
    fg=colors["text"],
    bg=colors["surface"],
    activebackground=colors["surface"],
    selectcolor=colors["surface2"],
    activeforeground=colors["text"],
    cursor="hand2",
    wraplength=S(280),
    justify=LEFT,
    highlightthickness=0,
    bd=0,
    relief=FLAT,
)
auto_check.pack(anchor=W)

# ── Footer (visible from start; shows locked-in config while running) ──
footer = Label(
    root_frame,
    text="",
    font=get_font(9),
    fg=colors["text_dim"],
    bg=colors["bg"],
    wraplength=S(360),
    justify=CENTER,
)
footer.pack(pady=(S(14), S(2)))
update_footer()

window.update_idletasks()
fit_window_to_content()
window.mainloop()
