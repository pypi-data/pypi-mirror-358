# CausalIQ Discovery: Causal Structure Learning Research

> ⚠️ **This repository is under active restructuring. Expect significant changes.**

This repository hosts the code and experimental infrastructure behind a series of academic papers on **Bayesian Network structure learning**, developed by [Ken Kitson](https://github.com/KenKitson) and collaborators.

It includes:
- New **structure learning algorithms** (e.g., Tabu-Stable)
- Tools for evaluating **stability** and **replicability**
- Integration of **human expertise** and **LLMs** in causal discovery
- A framework for **reproducing published figures and results**

---

## 📦 Project Goals

- Provide an installable Python package of reusable algorithms (`discovery/`)
- Separate large files (datasets, traces, charts) from GitHub via Zenodo/Hugging Face
- Offer a reproducibility system for experiments, figures, and tables from papers
- Support use on new datasets via a clean API

---

## 🔁 Reproducibility Workflow (Coming Soon)

Each figure or result in supported papers will be reproducible using three levels of access:

| Mode           | Description                                                     |
|----------------|-----------------------------------------------------------------|
| `--raw`        | Start from original datasets. Run structure learning from scratch. |
| `--intermediate` | Use precomputed learning traces (e.g., `.pkl.gz` files).        |
| `--results`    | Generate charts and tables from saved outputs. Fastest mode.     |

All required files will be **automatically downloaded** if not present locally.

---

## 📁 Planned Directory Structure

```
discovery/        # Python package: algorithms, loaders, scoring, etc.
data/             # Downloaded datasets (.csv.gz), not stored in Git
series/           # Experiment series definitions + learning traces (.pkl.gz)
charts/           # Output PNGs, CSVs, LaTeX tables
scripts/          # Zenodo downloaders, CLI runners
tests/            # Unit tests and reproducibility tests
examples/         # Minimal examples for new users
README.md
setup.py
```

---

## 📚 Related Papers

This repository supports experiments from:

- Kitson & Constantinou (2024a) – *Tabu-Stable for structure learning*
- Kitson & Constantinou (2024b) – *Variable ordering instability*
- Kitson et al. (2023) – *Survey of structure learning techniques*

More details, including DOIs and citation formats, will be added soon.

---

## 🚀 Example Usage (planned)

Figure reproduction from a paper (placeholder syntax):

```bash
python scripts/main.py --paper 2024b --figure fig5 --mode raw
python scripts/main.py --paper 2024b --figure fig5 --mode intermediate
python scripts/main.py --paper 2024b --figure fig5 --mode results
```

Or using `pytest`:

```bash
pytest -c papers.ini -s -k test_2024b_fig5
```

---

## 🔧 Using the Algorithms (planned)

Once packaged, install with:

```bash
pip install git+https://github.com/causal-iq/discovery
```

Use in your own code:

```python
from discovery.learning import tabustable
G = tabustable.learn_structure(df, score="bic", tabu_length=15)
```

---

## 📦 Future Plans

- [ ] Migrate large resources to Zenodo (datasets, traces, charts)
- [ ] Create reproducible series definitions in `/series/`
- [ ] Publish `discovery` to PyPI
- [ ] Add Hugging Face dataset mirror
- [ ] Provide CLI interface for figure/table generation

---

## 📜 License

This project is licensed under the MIT License.

---

## ✉️ Contact

For issues or collaboration, please open a GitHub issue or contact [Ken Kitson](https://github.com/KenKitson).
