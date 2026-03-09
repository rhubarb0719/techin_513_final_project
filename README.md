# Environment Setup

## Requirements
- Python 3.11 (required — librosa is not compatible with Python 3.13)
- Anaconda

---

## Step 1: Create Conda Environment

```bash
conda create -n techin513 python=3.11
conda activate techin513
```

## Step 2: Install Dependencies

```bash
conda install -c conda-forge librosa
pip install pandas scikit-learn matplotlib
```

## Step 3: Verify Installation

```bash
python -c "import librosa, pandas, sklearn, matplotlib; print('All good ✅')"
```

---

## Step 4: Open Notebook in VS Code

1. Open VS Code
2. Open the `Code/` folder
3. Click the kernel selector (top right of notebook)
4. Select **techin513**

---

## Project Structure

```
TECHIN_513_FINAL_PROJECT/
├── Code/
│   ├── Analysis module.ipynb    ← feature extraction + ML
│   └── ablation_study.ipynb     ← ablation study
├── Data/
│   ├── genres_original/         ← GTZAN audio files
│   └── features.csv             ← pre-extracted features (use this directly)
├── Documents/
└── README.md
```

---

## Notes

- `features.csv` is already generated — **no need to re-run Cell 7** (batch processing takes 15–30 min)
- Start from **Cell 9** (energy label + ML) when demoing
- Visual module: run `music_viz_final.py` separately with `python music_viz_final.py`