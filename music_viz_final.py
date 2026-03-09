"""
Team 18 — Music Energy Visualization
Visual mapping:
rectangles  ← RMS              : 8 columns, with heights pulsing to loudness and wave-like phase offsets
stars       ← spectral_flux    : 5–60 stars, with count and size changing with the spectrum, plus flicker
particles   ← energy_label     : Low = 15 (slow), Medium = 40 (moderate), High = 90 (fast)
color       ← spectral_centroid: all elements shift between cool and warm tones in sync

Usage:
  python music_viz_final.py
  → runs with synthetic demo data by default
  → set CSV_PATH = 'features.csv' to use real data
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
from matplotlib.collections import LineCollection
import warnings
warnings.filterwarnings('ignore')

# ══════════════════════════════════════════════════════════════
# 0. CONFIG
# ══════════════════════════════════════════════════════════════

CSV_PATH = None  # e.g. 'features.csv' — None = synthetic demo

# ══════════════════════════════════════════════════════════════
# 1. DATA LOADING
# ══════════════════════════════════════════════════════════════

def load_features_from_csv(path):
    """
    Load from CSV with columns: time, rms, centroid, flux, energy_label
    """
    try:
        import pandas as pd
    except ImportError:
        raise ImportError("pandas required. Run: pip install pandas")
    df = pd.read_csv(path)
    required = {'rms', 'centroid', 'flux', 'energy_label'}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"CSV missing columns: {missing}")
    print(f"Loaded {len(df)} rows from '{path}'")
    return (df['rms'].to_numpy(float), df['centroid'].to_numpy(float),
            df['flux'].to_numpy(float), df['energy_label'].tolist())


def generate_demo_data(n_frames=360):
    """Smooth synthetic demo data."""
    t = np.linspace(0, 5 * np.pi, n_frames)
    rms      = np.clip(0.5 + 0.42*np.sin(t*0.6)   + 0.08*np.random.randn(n_frames), 0.05, 1)
    centroid = np.clip(0.5 + 0.44*np.sin(t*0.35+1.2) + 0.04*np.random.randn(n_frames), 0, 1)
    flux     = np.clip(0.5 + 0.44*np.sin(t*1.0+2.5)  + 0.04*np.random.randn(n_frames), 0, 1)
    labels = []
    for i in range(n_frames):
        p = (i / n_frames) * 4
        if   p < 1: labels.append('Low')
        elif p < 2: labels.append('Medium')
        elif p < 3: labels.append('High')
        else:       labels.append('Medium')
    return rms, centroid, flux, labels


# ── Auto-select data source ───────────────────────────────────
if CSV_PATH is not None:
    rms_values, centroid_values, flux_values, energy_labels = load_features_from_csv(CSV_PATH)
    print("Using real CSV data ✅")
else:
    rms_values, centroid_values, flux_values, energy_labels = generate_demo_data()
    print("Using synthetic demo data ✅  (set CSV_PATH to use real data)")


# ══════════════════════════════════════════════════════════════
# 2. NORMALIZATION
# ══════════════════════════════════════════════════════════════

def normalize(a):
    lo, hi = a.min(), a.max()
    return (a - lo) / (hi - lo + 1e-8)

def smooth(a, w=8):
    return np.convolve(a, np.ones(w)/w, mode='same')

rms_n      = smooth(normalize(np.array(rms_values,      float)))
centroid_n = smooth(normalize(np.array(centroid_values, float)))
flux_n     = smooth(normalize(np.array(flux_values,     float)))
N_FRAMES   = len(rms_n)

# energy_label → particle count + speed
PARTICLE_MAP = {'Low': (15, 0.004), 'Medium': (40, 0.009), 'High': (90, 0.018)}


# ══════════════════════════════════════════════════════════════
# 3. COLOR SYSTEM
# centroid_n 0→1: deep blue/violet → cyan → magenta → neon pink → warm orange
# ALL visual elements share this color temperature
# ══════════════════════════════════════════════════════════════

_CMAP_DEF = [
    (0.00, '#020010'),   # near-black
    (0.12, '#001888'),   # deep blue
    (0.26, '#0044ee'),   # electric blue
    (0.42, '#4400bb'),   # indigo
    (0.56, '#8800cc'),   # violet
    (0.68, '#cc0088'),   # magenta / pink
    (0.80, '#ff2255'),   # hot pink
    (0.88, '#ff6600'),   # orange
    (1.00, '#ffcc00'),   # gold
]

# ── Per-label hue window ─────────────────────────────────────
# centroid_n [0,1] is remapped into the label's color band.
# Low → blue/indigo  (0.26–0.50)
# Medium → orange/gold (0.86–1.00)
# High → violet/pink  (0.56–0.80)
_LABEL_HUE = {
    'Low':    (0.18, 0.38),
    'Medium': (0.50, 0.68),
    'High':   (0.82, 1.00),
}

def centroid_to_hue(centroid_n, label):
    lo, hi = _LABEL_HUE[label]
    return lo + centroid_n * (hi - lo)

def _build_cmap():
    pos = [c[0] for c in _CMAP_DEF]
    rgb = [mcolors.to_rgb(c[1]) for c in _CMAP_DEF]
    d = {'red': [], 'green': [], 'blue': []}
    for p, (r, g, b) in zip(pos, rgb):
        d['red'  ].append((p, r, r))
        d['green'].append((p, g, g))
        d['blue' ].append((p, b, b))
    return mcolors.LinearSegmentedColormap('neon', d)

CMAP = _build_cmap()

def gc(hue, alpha=1.0):
    """Get RGBA from normalized hue [0,1]."""
    r, g, b, _ = CMAP(np.clip(hue, 0, 1))
    return (r, g, b, np.clip(alpha, 0, 1))


# ══════════════════════════════════════════════════════════════
# 4. RECTANGLES  (RMS → height, wave phase offset per column)
# 8 vertical columns, heights pulse with RMS,
# each column has a slight sine phase offset → wave ripple effect
# ══════════════════════════════════════════════════════════════

N_COLS   = 8
COL_XS   = np.linspace(0.08, 0.92, N_COLS)   # x centers of columns
COL_W    = 0.07                                # column width (axes units)
BASE_Y   = 0.12                                # bottom anchor
MAX_H    = 0.55                                # max height at RMS=1

def draw_rectangles(ax, rms, centroid, t):
    """
    8 columns, each with a sine wave phase offset.
    Height = base_height * (1 + phase_offset_sine)
    Two mirrored rectangles per column (top + bottom) for symmetry.
    """
    for i, cx in enumerate(COL_XS):
        # Wave phase: each column offset by π/4, slow drift over time
        phase   = t * 1.8 + i * (np.pi / 4)
        h_scale = 0.65 + 0.35 * np.sin(phase)          # oscillates 0.30 → 1.0
        height  = (0.10 + rms * MAX_H) * h_scale
        height  = max(height, 0.03)

        # Slight hue shift across columns (spread centroid ±0.15)
        hue = np.clip(centroid + (i / N_COLS - 0.5) * 0.30, 0, 1)

        # ── Main rectangle (grows upward from baseline) ──
        rect = mpatches.FancyBboxPatch(
            (cx - COL_W/2, BASE_Y),
            COL_W, height,
            boxstyle="round,pad=0.005",
            facecolor=gc(hue, 0.75),
            edgecolor=gc(hue, 0.95),
            linewidth=0.8,
            zorder=10
        )
        ax.add_patch(rect)

        # ── Soft glow halo behind each rectangle ──
        glow = mpatches.FancyBboxPatch(
            (cx - COL_W*1.1, BASE_Y),
            COL_W*2.2, height,
            boxstyle="round,pad=0.01",
            facecolor=gc(hue, 0.10),
            edgecolor='none',
            zorder=9
        )
        ax.add_patch(glow)

        # ── Bright top edge highlight ──
        top_y = BASE_Y + height
        ax.plot([cx - COL_W/2 + 0.005, cx + COL_W/2 - 0.005],
                [top_y, top_y],
                color=gc(hue, 0.95), linewidth=1.5, zorder=11)

        # ── Reflection below baseline (mirrored, faint) ──
        ref_h = height * 0.35
        ref = mpatches.FancyBboxPatch(
            (cx - COL_W/2, BASE_Y - ref_h),
            COL_W, ref_h,
            boxstyle="round,pad=0.005",
            facecolor=gc(hue, 0.18),
            edgecolor='none',
            zorder=8
        )
        ax.add_patch(ref)


# ══════════════════════════════════════════════════════════════
# 5. STARS  (flux → count 5~60, size, flicker)
# Scattered across upper canvas area
# ══════════════════════════════════════════════════════════════

# Pre-generate stable star positions (same seed = same layout each frame)
_STAR_RNG  = np.random.default_rng(99)
_STAR_XS   = _STAR_RNG.uniform(0.03, 0.97, 60)
_STAR_YS   = _STAR_RNG.uniform(0.55, 0.97, 60)   # upper half of canvas
_STAR_BASE = _STAR_RNG.uniform(0.3, 1.0, 60)      # base brightness

def draw_stars(ax, flux, centroid, t):
    """
    Number of visible stars: 5 + int(flux * 55)  → 5 to 60
    Size + alpha flicker independently per star.
    """
    n_stars = int(5 + flux * 55)

    for i in range(n_stars):
        x, y   = _STAR_XS[i], _STAR_YS[i]
        # Flicker: each star has its own frequency
        flicker = 0.5 + 0.5 * np.sin(t * (2.0 + i * 0.3) + i * 1.7)
        size    = (8 + flux * 55) * _STAR_BASE[i] * (0.6 + 0.4 * flicker)
        alpha   = 0.35 + 0.55 * flicker * _STAR_BASE[i]

        hue = np.clip(centroid + _STAR_BASE[i] * 0.2 - 0.1, 0, 1)

        # Draw 4-point star shape using scatter marker
        ax.scatter(x, y, s=size, c=[gc(hue, alpha)],
                   marker='*', zorder=15, linewidths=0)

        # Soft glow around bright stars
        if flicker > 0.7:
            ax.scatter(x, y, s=size * 5, c=[gc(hue, alpha * 0.12)],
                       marker='o', zorder=14, linewidths=0)


# ══════════════════════════════════════════════════════════════
# 6. PARTICLES  (energy_label → count + speed)
# Vertical rising streaks — like light particles floating up
# Low=15 slow,  Medium=40 medium,  High=90 fast
# ══════════════════════════════════════════════════════════════

class ParticleSystem:
    def __init__(self, max_n=90):
        self.max_n = max_n
        self.pool  = [self._new(startup=True) for _ in range(max_n)]

    def _new(self, startup=False):
        return {
            'x':     np.random.uniform(0.02, 0.98),
            'y':     np.random.uniform(0.0, 1.0) if startup else np.random.uniform(-0.05, 0.1),
            'vy':    np.random.uniform(0.003, 0.010),   # base upward speed
            'size':  np.random.uniform(6, 22),
            'alpha': np.random.uniform(0.25, 0.70),
            'hue':   np.random.uniform(0.0, 1.0),
            'drift': np.random.uniform(-0.0006, 0.0006),
        }

    def update(self, n_active, speed_mult, centroid):
        for i, p in enumerate(self.pool[:n_active]):
            p['y']    += p['vy'] * speed_mult
            p['x']     = np.clip(p['x'] + p['drift'], 0.02, 0.98)
            p['hue']   = np.clip(centroid + np.random.randn() * 0.08, 0, 1)
            if p['y'] > 1.05:
                self.pool[i] = self._new()

    def render(self, ax, n_active, centroid):
        xs, ys, sizes, colors = [], [], [], []
        for p in self.pool[:n_active]:
            xs.append(p['x'])
            ys.append(p['y'])
            sizes.append(p['size'])
            colors.append(gc(p['hue'], p['alpha']))

        if xs:
            ax.scatter(xs, ys, s=sizes, c=colors,
                       marker='o', zorder=6, linewidths=0)
            # Soft glow version
            glow_colors = [gc(p['hue'], p['alpha'] * 0.15) for p in self.pool[:n_active]]
            ax.scatter(xs, ys, s=[s*6 for s in sizes], c=glow_colors,
                       marker='o', zorder=5, linewidths=0)


# ══════════════════════════════════════════════════════════════
# 7. BACKGROUND
# Deep dark gradient, subtle color tint from centroid
# ══════════════════════════════════════════════════════════════

def draw_background(ax, hue, t):
    ax.set_facecolor('#000000')
    # Subtle ambient color wash in upper area
    for i in range(12):
        frac  = i / 12
        alpha = 0.025 * (1 - frac)
        ax.add_patch(plt.Circle(
            (0.5, 0.75), 0.7*(1-frac*0.5),
            color=gc(hue, alpha),
            transform=ax.transAxes, zorder=0
        ))

    # Horizontal floor glow under rectangles
    for i in range(6):
        frac = i / 6
        ax.add_patch(mpatches.FancyBboxPatch(
            (0.0, BASE_Y - 0.015 - frac*0.02),
            1.0, 0.012,
            boxstyle="square,pad=0",
            facecolor=gc(hue, 0.04*(1-frac)),
            edgecolor='none',
            zorder=3, transform=ax.transAxes
        ))


# ══════════════════════════════════════════════════════════════
# 8. MAIN ANIMATION
# ══════════════════════════════════════════════════════════════

PARTICLE_SYS = ParticleSystem(max_n=90)

fig, ax = plt.subplots(figsize=(11, 7))
fig.patch.set_facecolor('#000000')
ax.set_xlim(0, 1); ax.set_ylim(0, 1)
ax.set_aspect('auto'); ax.axis('off')
fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

_T = [0.0]

def update(frame):
    ax.cla()
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_aspect('auto'); ax.axis('off')

    idx      = frame % N_FRAMES
    rms      = float(rms_n[idx])
    centroid = float(centroid_n[idx])
    flux     = float(flux_n[idx])
    label    = energy_labels[idx]

    n_particles, p_speed = PARTICLE_MAP[label]
    _T[0] += 0.04 * {'Low': 0.5, 'Medium': 1.0, 'High': 2.0}[label]

    # Remap centroid into label's color window
    hue = centroid_to_hue(centroid, label)

    # ── Background ──
    draw_background(ax, hue, _T[0])

    # ── Particles (behind rectangles) ──
    PARTICLE_SYS.update(n_particles, p_speed * 60, hue)
    PARTICLE_SYS.render(ax, n_particles, hue)

    # ── Rectangles ──
    draw_rectangles(ax, rms, hue, _T[0])

    # ── Stars ──
    draw_stars(ax, flux, hue, _T[0])

    # ── Label HUD (neon + readable) ──
    lc = {'Low': '#00E5FF', 'Medium': '#CCFF00', 'High': '#FF2DFF'}
    txt = ax.text(0.03, 0.97, label.upper(),
                  ha='left', va='top', fontsize=16, fontweight='bold',
                  color=lc[label], alpha=0.95,
                  fontfamily='monospace', transform=ax.transAxes, zorder=30)
    txt.set_path_effects([pe.Stroke(linewidth=2.2, foreground='#000000'), pe.Normal()])

    return []


ani = animation.FuncAnimation(
    fig, update,
    frames=N_FRAMES,
    interval=45,
    blit=False,
    repeat=True
)

plt.show()
