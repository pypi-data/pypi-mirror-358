# nb2latex

Convert multiple Jupyter notebooks into a single LaTeX document and PDF.

## Overview

`nb2latex` is a lightweight Python CLI tool that takes multiple `.ipynb` files and combines them into one clean LaTeX document. It extracts the main body of each .tex file produced from the corresponding .ipynb file using `nbconvert` and stitches them together into a single .tex file which is then compiled by `pdflatex` to output a PDF. A table of contents and title page are also included.

## How it works

- Converts selected `.ipynb` notebooks to LaTeX using `nbconvert`.
- Strips unnecessary LaTeX preamble, begin{document}, and end{document} in each .tex file.
- Combines main bodies into one .tex document and uses the preamble from `nbconvert`.
- Adds title page and table of contents automatically.
- Compiles the final `.tex` to PDF using `pdflatex`.
- Cleans up excess files post-compile.


## Requirements

- Python >= 3.12 
- Pandoc (required for `nbconvert`)
- A LaTeX distribution providing `pdflatex` on PATH (e.g MiKTeX or TeX Live)

Install dependencies:

```bash
pip install nb2latex
```

## (Optional environment)

You can also recreate the environment using Micromamba/Conda and the provided environment.yml to install all dependencies except LaTeX distribution.

Micromamba:
```bash
micromamba create -f environment.yml
micromamba activate nb2latexEnv
```
Or Conda:
```bash
conda env create -f environment.yml
conda activate nb2latexEnv
```

## Usage

```bash
nb2latex --title "LaTeX notebooks" notebook1.ipynb notebook2.ipynb notebook3.ipynb
```

