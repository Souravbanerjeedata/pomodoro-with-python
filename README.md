# 🍅 Pomodoro Timer

A clean, modern desktop Pomodoro timer built with pure Python and Tkinter.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## Features

- **Classic Pomodoro cycle**
  - 25 minutes of focused work
  - 5-minute short break
  - 20-minute long break after 4 work sessions
- **Modern dark UI** with refined color palette and clear visual hierarchy
- **Session tracking** with check marks after each completed work block
- **Smart button states** – Start is disabled while a timer is running
- **Robust path handling** – works no matter where you launch the script from
- **Zero extra dependencies** – only uses the Python standard library + Tkinter

---

## Screenshots

The app features a deep navy background, a vibrant tomato illustration, large readable timer, and clearly colored states:

| State        | Color / Meaning          |
|--------------|--------------------------|
| Focus Time   | Mint green               |
| Short Break  | Soft pink                |
| Long Break   | Strong red               |
| Idle         | Neutral off-white        |

---

## Requirements

- Python 3.8 or higher
- Tkinter (comes pre-installed with most Python distributions)

> **Note:** On some Linux systems you may need to install Tkinter separately:
> ```bash
> sudo apt install python3-tk
> ```

---

## Installation & Usage

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

That's it — no `pip install` required.

---

## How to Use

1. Click **START** to begin the first focus session.
2. The timer will automatically cycle through:
   - Work → Short Break → Work → Short Break → Work → Short Break → Work → Long Break
3. After each completed work session a ✓ appears.
4. Click **RESET** at any time to stop the timer and return to the idle state.

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

You can easily change the timer lengths at the top of `main.py`:

```python
WORK_MIN = 25
SHORT_BREAK_MIN = 5
LONG_BREAK_MIN = 20
```

Want a different look? Adjust the color constants in the same section.

---

## Improvements over the original

- Modern dark theme with professional color palette
- Clear status messages that change with each phase
- Session counter (“Session X / 4”)
- Buttons that properly enable/disable
- Consistent time formatting (`05:09` instead of `5:9`)
- Cleaner code structure and safer global state handling
- Robust file path resolution using `pathlib`
- Better typography and spacing

---

## License

MIT License – feel free to use, modify, and share.

---

Made with ❤️ and a lot of focus sessions.
