# Uneven Automation: AI's Impact on Software Engineering Varies by Task Difficulty and Data Availability

## Overview
We examines the impact of AI on software engineering tasks by using
Stack Overflow questions as a proxy, based on publicly available archival data.

---

## Data Availability
**Raw Data**
* The raw data analyzed in this study are publicly available from the Stack Exchange
   * Data Dump: ![https://archive.org/details/stackexchange]
   * Release used in this study: December 3, 2023
Due to the large size of the Stack Exchange Data Dump, the raw data are not redistributed in this repository.

**Processed Data**
* This repository provides processed datasets sufficient to reproduce all figures and tables reported in the manuscript.
* These datasets are located in the data/ directory and were generated from the December 3, 2023 Stack Exchange Data Dump following the preprocessing steps implemented in this repository.

## Reproducibility Scope
* Full replication from raw Stack Exchange data requires downloading the original Stack Exchange Data Dump and running the preprocessing scripts provided in this repository.
* To facilitate reproducibility without requiring access to the full raw dataset, we provide processed data files that allow replication of All main figures

---

## Repository Structure
```text
.   
├── data/                      # Processed datasets for reproducing figures and tables
├── data_availability/         # Script for measuring data availability
├── difficulty/                # Script for measuring difficulty
├── submission/                # Script for visualizing the figures in manuscript
├── util/                      # Library for commonly used function 
├── requirements.txt           # Python dependencies
└── README.md
```
---

## Software and Code Documentation

### System requirements

### Operating system
 *The code has been tested on the following operating systems:
- Ubuntu 22.04 LTS

### Software dependencies
* Python 3.10.12
* Required Python packages are listed in `requirements.txt`

### Computational Environment

* Large language model inference used to annotate the difficulty of Stack Overflow questions was conducted on a multi-GPU workstation with the following specifications:

- GPU: NVIDIA RTX A5000 (24 GB VRAM) × 4
- CUDA version: 12.9
- NVIDIA driver version: 575.57.08

* Equivalent GPU configurations with comparable memory capacity are sufficient to reproduce the analyses.

---

## Large Language Model Configuration

* Large language models are used to measure task difficulty and related constructs.

- Model: LLaMA 3.1 70B Instruct
- Inference framework: ollama
- Decoding parameters:
  - Temperature: 0.01
  - Maximum number of generated tokens (`num_predict`): 100
  - Context length (`num_ctx`): 4096
  - Stop tokens: `<s>`, `</s>`

No additional decoding or sampling parameters were used.

---

## Installation guide

### Instructions
1. Clone the repository:
   ```bash
   git clone https://github.com/myokyunghan/uneven_automation.git
   cd uneven_automation
   ```
2. Construct python virtual environment
   ```bash
   # in the 'uneven_automation' directory
   brew install pyenv
   echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
   echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
   echo 'eval "$(pyenv init --path)"' >> ~/.zshrc
   echo 'eval "$(pyenv init -)"' >> ~/.zshrc
   source ~/.zshrc
   
   pyenv install 3.10.12
   pyenv versions
   ```
3. Activate the virtual environment 
   ```bash
   # in the 'uneven_automation' directory
   pyenv local 3.10.12
   python3 -m venv venv_uneven_automation
   source venv_uneven_automation/bin/activate
   ```
   
4. Install dependencies
   ```bash
   # in the 'uneven_automation' directory
   pip install -r requirements.txt
   ```
   * Installation typically takes approximately 10-15 minutes on a standard desktop comuter, excluding GPU driver and CUDA installation.

---

## Execution Guide
* All figures and tables reported in the manuscript can be reproduced using the
  processed data provided in this repository.
* To improve transparency and reproducibility, the analysis and visualization
  pipelines are provided as **Jupyter notebooks (`.ipynb`)** in the `submission/`
  directory.
* These notebooks contain executable code, intermediate outputs, and inline
  documentation, allowing readers to inspect and reproduce each step of the
  analysis interactively.

**Examples:**
- `submission/C_Result_Fig1.ipynb`
- `submission/C_Result_Fig2_1.ipynb`
- `submission/C_Result_Fig2_2.ipynb`  
  (The results from `C_Result_Fig2_1.ipynb` and `C_Result_Fig2_2.ipynb` are combined
  for ease of interpretation.)

* Each notebook is self-contained and can be executed cell by cell using the
  processed datasets included in this repository.






