# 🍅 Pomodoro Timer

A clean, modern desktop Pomodoro timer built with pure Python and Tkinter.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## Download the App

**No Python required.** Download the ready-to-run Windows executable:

➡️ **[Download Pomodoro.exe](https://drive.google.com/file/d/12BpsugKvkXF6J2JDDiVeO1Vug4IE8Oz-/view)**

Just download, double-click, and start focusing.

---

## Features


- **Classic Pomodoro cycle**
  - 25 minutes of focused work
  - 5-minute short break
  - 20-minute long break after 4 work sessions
- **Pause & Resume** – interrupt a session and continue exactly where you left off
- **Sound notification** when a session ends (works on Windows, macOS and Linux)
- **Light / Dark theme toggle** – switch instantly with one click
- **Modern UI** with refined color palette and clear visual hierarchy
- **Session tracking** with check marks after each completed work block
- **Smart button states** – controls enable/disable automatically
- **Zero extra dependencies** – only Python standard library + Tkinter

---

## Themes

| Theme | Description |
|-------|-------------|
| **Dark** (default) | Deep navy background, mint / pink / red accents |
| **Light** | Soft cream background (classic Pomodoro feel) |

Phase colors stay consistent in both themes:
- Focus → Green
- Short Break → Pink
- Long Break → Red

---

## Requirements

- Python 3.8 or higher
- Tkinter (comes pre-installed with most Python distributions)

> **Linux note:** If Tkinter is missing:
> ```bash
> sudo apt install python3-tk
> ```

---

## Installation & Usage

### Option 1 – Download the executable (easiest)
1. Go to the [Download link](https://drive.google.com/file/d/12BpsugKvkXF6J2JDDiVeO1Vug4IE8Oz-/view)
2. Download `Pomodoro.exe`
3. Double-click to run (no Python needed)

### Option 2 – Run from source
1. Clone the repository:
   ```bash
   git clone https://github.com/Souravbanerjeedata/pomodoro-with-python.git
   cd pomodoro-with-python
   ```
2. Make sure `tomato.png` is in the same folder as `main.py`.
3. Run the app:
   ```bash
   python main.py
   ```

No `pip install` required.

---

## How to Use

| Button | Action |
|--------|--------|
| **START** | Begin a new focus session |
| **PAUSE** | Temporarily stop the current countdown |
| **RESUME** | Continue from the exact remaining time |
| **RESET** | Stop everything and return to idle state |
| **☀️ Light / 🌙 Dark** | Toggle between light and dark themes |

The timer automatically cycles:

```
Work → Short Break → Work → Short Break → Work → Short Break → Work → Long Break
```

A short sound plays whenever a session finishes.

---

## Project Structure

```
pomodoro-with-python/
├── main.py          # Main application
├── tomato.png       # Tomato illustration
└── README.md        # This file
```

---

## Customization

Open `main.py` and change the constants at the top:

```python
WORK_MIN = 25
SHORT_BREAK_MIN = 5
LONG_BREAK_MIN = 20
```

You can also tweak the color values inside the `THEMES` dictionary if you want a completely custom look.

---

## Technical Notes

### Sound
- **Windows** → `winsound` (built-in)
- **macOS** → system Glass sound via `afplay`
- **Linux** → tries common free-desktop sounds, falls back to terminal bell

### Pause / Resume
The remaining seconds are stored when you pause, so resuming continues from the exact point you stopped.

### Theme switching
All widgets are recolored live — no restart needed.

---

## Improvements over the original course project

- Pause & Resume functionality
- Cross-platform sound notifications
- Light / Dark theme toggle
- Modern dark theme by default + classic light theme
- Clear status messages that change with each phase
- Session counter (“Session X / 4”)
- Proper button state management
- Consistent `MM:SS` time formatting
- Robust file path resolution with `pathlib`
- Cleaner global state handling

---

## License

MIT License – feel free to use, modify, and share.

---

Made with ❤️ and a lot of focus sessions.
