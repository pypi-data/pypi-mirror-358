# 🧼 datacleanx

**datacleanx** is a fast, CLI-first data cleaning engine for tabular datasets. It's designed for machine learning practitioners and data engineers who want to automate cleaning workflows efficiently using a single command-line interface.

---

## 🚀 Why datacleanx?

- 🔁 Automates repetitive cleaning steps
- 📦 Works out-of-the-box with CSV files
- 📁 Outputs timestamped cleaned files and reports
- 🐳 Docker-ready for CI/CD and containerized workflows
- 🧪 Includes tests and reports for reproducibility

---

## 🔧 Features

- ✅ Imputation: `mean`, `median`, `mode`
- ✅ Encoding: `label`, `onehot`
- ✅ Outlier removal using IQR
- ✅ Feature scaling: `standard`, `minmax`, `robust`
- ✅ Auto-saves cleaned data to `outputs/`
- ✅ Saves reports as structured JSON
- ✅ CLI-first design, easily scriptable
- ✅ Docker and Poetry integration

---

## 📦 Installation

### ✅ Option 1: From PyPI

```bash
pip install datacleanx
