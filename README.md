# Music-to-Imagine: An ML-Based Music Energy Visualizer for Deaf and Hard of Hearing Users

**TECHIN 513 Final Project — Team 18**
Yilu Huang · Taya Li | University of Washington

---

## Overview

Music-to-Imagine is a system that automatically classifies the perceptual energy level of a music track into three categories — **Low**, **Medium**, and **High** — and maps the result to a real-time visual animation. The goal is to help Deaf and Hard of Hearing (DHH) users quickly assess the energetic character of unfamiliar music without sustained listening.

---

## Project Structure

```
TECHIN_513_FINAL_PROJECT/
├── Code/
│   ├── Analysis module.ipynb    ← Feature extraction + ML classification
│   └── ablation_study.ipynb     ← Ablation study
├── Data/
│   ├── genres_original/         ← GTZAN audio files (not included in repo)
│   ├── features.csv             ← Pre-extracted features (999 tracks × 18 features)
│   └── figures/                 ← Generated plots
├── music_viz_final.py           ← Real-time visualization
└── README.md
```

---

## Pipeline

```
GTZAN Audio (.wav)
    ↓  Feature Extraction (librosa)
features.csv — 18 features per track
    ↓  Energy Labeling (RMS + Tempo dual-threshold)
Low / Medium / High labels
    ↓  ML Classification (SVM, RBF kernel)
Predicted energy label
    ↓  Visual Mapping
Real-time animation
```

---

## Features (18 total)

| Feature | Dimension | Count |
|---|---|---|
| RMS Energy | Time-domain | 1 |
| Zero Crossing Rate | Time-domain | 1 |
| Spectral Centroid | Frequency-domain | 1 |
| Spectral Flux | Frequency-domain | 1 |
| Tempo (BPM) | Rhythmic | 1 |
| MFCC 1–13 | Timbral | 13 |

---

## Visual Mapping

| Audio Feature | Visual Element | Behavior |
|---|---|---|
| Energy Label | Particles | Low=15 slow · Medium=40 · High=90 fast |
| RMS Energy | Rectangles | Height + brightness |
| Spectral Flux | Stars | Count (5–60) + flicker rate |
| Spectral Centroid | Color/Hue | Low=blue · Medium=violet · High=orange/gold |

---

## Results

| Model | Accuracy |
|---|---|
| Logistic Regression | 82.0% |
| **SVM (RBF kernel)** | **84.5%** ✅ |
| Random Forest | 99.0% ⚠️ overfitting |

SVM per-class F1: Low 0.88 · Medium 0.79 · High 0.86

**Ablation study**: Tempo alone contributes a +29% accuracy jump (60.5% → 89.5%).

---

## Setup

See [SETUP.md](SETUP.md) for full environment installation instructions.

**Quick start:**
```bash
conda create -n techin513 python=3.11
conda activate techin513
conda install -c conda-forge librosa
pip install pandas scikit-learn matplotlib
```

---

## Usage

**Run visualization (demo mode):**
```bash
python music_viz_final.py
```

**Run with real data:**
Set `CSV_PATH = '../Data/features.csv'` in `music_viz_final.py`, then run.

**Run analysis notebook:**
Open `Code/Analysis module.ipynb` in VS Code or Jupyter, select `techin513` kernel.
Skip Cell 7 (batch processing) — `features.csv` is already generated.

---

## Dataset

GTZAN Dataset — 999 tracks, 10 genres, 30s clips at 22,050 Hz mono WAV.
Source: [Kaggle — GTZAN Music Genre Classification](https://www.kaggle.com/datasets/andradaolteanu/gtzan-dataset-music-genre-classification)

> Note: Audio files are not included in this repository due to size. Download from Kaggle and place in `Data/genres_original/`.

---

## References

- Deja et al. (2020). ViTune. NIME.
- Nanayakkara et al. (2013). Human-Computer Interaction, 28(2).
- Wang et al. (2023). AAAI, vol. 37.
- Tzanetakis & Cook (2002). IEEE Transactions on Speech and Audio Processing.
- Valdez & Mehrabian (1994). Journal of Experimental Psychology: General.