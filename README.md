# Formula 1 Pixel Racing
Achieved: 69/70 or A* grade.

**Formula 1 Pixel Racing** - a retro-inspired 2D pixel art racing game I developed for my A-Level OCR Computer Science Non-Examined Assessment (NEA) project. Designed for racing enthusiasts and strategists, I developed this game to simulate the precision, strategy and speed that encompasses Formula 1 in the form of a simple 2D pixel art racing game.

The entire game is implemented in a **single Python file (`formula1v78.py`)**, reflecting its origins as a solo project and OCR A-Level Computer Science NEA (scored **69/70**), later extended with performance optimisations and additional systems.

This repository presents the project in its original architectural style, prioritising **clarity, performance, and practical engineering decisions** over artificial modularisation.

---

## Key Features

- Pure **Python + Pygame** (no external engines or physics libraries)
- Custom **rotation system** using precomputed lookup tables (trig-equivalent)
- **Tile-based map rendering with culling** (only visible tiles are drawn)
- **Dynamic camera** that looks ahead based on velocity
- Arcade-style vehicle handling with traction and inertia
- **Tyre wear system** affecting grip, displayed via HUD
- Optimised for stable **60 FPS** on modest hardware
- 100% original visuals and audio

---

## Why a single file?

This project intentionally remains in a single file:

- It began as a constrained academic project
- Systems were developed iteratively and tightly coupled
- Performance was prioritised over abstraction
- Refactoring into modules was unnecessary for the scope

If continued as a larger project, the codebase could be split cleanly into
`rendering`, `physics`, `vehicle`, and `track` modules — but this repository
preserves the **authentic development history** of the project.

---

## Running the game

### Requirements
- Python 3.10+
- Pygame 2.x

### Install dependencies
```bash
pip install -r requirements.txt
