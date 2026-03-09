# Team 18 — Music Energy Visualization

A real-time music energy visualizer that maps audio features to abstract visual elements, designed to help Deaf and Hard of Hearing (DHH) users assess music energy at a glance.

---

## Visual Mapping

| Visual Element | Audio Feature | How It Works |
|---|---|---|
| 🟥 Rectangles | RMS (loudness) | Height = louder → taller |
| ⭐ Stars | Spectral Flux | Count + flicker = more spectral change → more active stars |
| 🔵 Particles | Energy Label | Density + speed = Low → few/slow, High → many/fast |
| 🎨 Color | Spectral Centroid | Hue shifts within label's color window |

---

## Feature Explanations

### RMS → Rectangles
**RMS (Root Mean Square)** measures the overall loudness/energy of a track — the average power of the audio signal.

- High RMS → rectangles are **taller and brighter**
- Low RMS → rectangles are **shorter and dimmer**
- An animated sine wave (phase-offset per column) creates a ripple effect across the 8 columns, making the composition feel alive rather than static
- The wave is purely decorative; RMS is the semantic driver

### Spectral Flux → Stars
**Spectral Flux** measures how rapidly the frequency spectrum changes between frames — high flux means the timbre and texture of the music is shifting frequently (e.g. drums, electronic music).

- High flux → **more stars, larger, faster flicker**
- Low flux → **fewer stars, smaller, slower shimmer**
- Star count ranges from 5 to 60
- Each star has an independent flicker frequency for an organic feel
- Stars are concentrated in the upper half of the canvas

### Energy Label → Particles
**Energy Label** (Low / Medium / High) is a song-level classification derived from RMS and Tempo. It is the primary semantic layer of the visualization — viewers should immediately sense the energy state from the particles alone.

| Label | Particle Count | Speed |
|---|---|---|
| Low | 15 | Slow drift |
| Medium | 40 | Moderate rise |
| High | 90 | Fast ascent |

Particles rise upward continuously and respawn from the bottom, creating a sense of energy flowing through the scene.

### Spectral Centroid → Color
**Spectral Centroid** is the "center of mass" of the frequency spectrum — a high centroid means the sound is brighter/trebly, a low centroid means it is darker/bassy.

Each energy label has its own dedicated color window, so the color identity is unambiguous:

| Label | Color Range | Hue Window |
|---|---|---|
| Low | Blue → Indigo | 0.18 – 0.38 |
| Medium | Violet → Magenta | 0.50 – 0.68 |
| High | Pink → Orange/Gold | 0.82 – 1.00 |

Within each window, spectral centroid shifts the hue — brighter sound = warmer tint within the label's range. All visual elements (rectangles, stars, particles, background) share the same hue.

---

## Energy Level Visual Identity

| | LOW | MEDIUM | HIGH |
|---|---|---|---|
| **Feel** | Calm, sparse, dim | Balanced, moderate | Intense, dense, bright |
| **Color** | Cool blue / indigo | Violet / magenta | Warm pink / orange / gold |
| **Rectangles** | Short | Mid-height | Tall |
| **Stars** | Few, slow flicker | Moderate | Many, rapid shimmer |
| **Particles** | 15, slow drift | 40, moderate | 90, fast ascent |
| **Background** | Dark, minimal glow | Soft ambient wash | Strong color field |

---

## Usage

```bash
# Run with synthetic demo data
python music_viz_final.py

# Run with real song features
Set CSV_PATH = 'features.csv' at the top of the file


### CSV Format
The input CSV must contain these columns:

| Column | Type | Description |
|---|---|---|
| `rms` | float | Root mean square energy |
| `centroid` | float | Spectral centroid |
| `flux` | float | Spectral flux |
| `energy_label` | string | `Low` / `Medium` / `High` |