# Music-to-Imagine System (Team 18)

ML-based music visual tool. The project is split into two branches:

| Branch | Content |
|--------|--------|
| **`analysis`** | DSP feature extraction + SVM energy classification (Low/Medium/High) |
| **`visual`** | Visual output mapping (待开发) |

---

## Analysis branch (`analysis`)

A music energy classification system that extracts DSP features from audio and uses SVM to classify songs into **Low** / **Medium** / **High** energy states.

- **Tech stack:** Python, librosa, scikit-learn, matplotlib, pandas  
- **Dataset:** [GTZAN](https://www.kaggle.com/datasets/andradaolteanu/gtzan-dataset-music-genre-classification) (not included; download from Kaggle).  
- **How to run:**  
  1. `git checkout analysis`  
  2. `pip install librosa scikit-learn matplotlib pandas`  
  3. Open `513Final.ipynb` and run all cells.

---

## Visual branch (`visual`)

Visualization of classification results — 视觉部分由队友开发中。
