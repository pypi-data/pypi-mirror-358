# NP-SAM

## Introduction

In this project we propose an easily implementable workflow for a fast, accurate and seamless experience of segmentation of nanoparticles.

The project's experience can be significantly enhanced with the presence of a CUDA-compatible device; alternatively, Google Colab can be utilized if such a device is not accessible. For a quick access to the program and a CUDA-GPU try our Google Colab notebook. <br>
[![Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1it8TbVeeKUiJZXn8HThiUK7epAq5EZTK?usp=sharing)

## Installation
### Windows Application
Download one of the .zip files below and extract the content. Afterwards, simply run the .exe file.

NP-SAM for PCs with CUDA compatible graphics card (2.5 GB) here: [NP-SAM with CUDA](https://sciencedata.dk/shared/5c1e737619f0b849cf66e47ea123c4a5)

NP-SAM for PCs without CUDA compatible graphics card (500 MB) here: [NP-SAM without CUDA](https://sciencedata.dk/shared/5824fef552b6b7e99a25966370c92e01)

### Python package
Optional: Create a new conda environment called `npsam` (line 1) and activate it (line 2). This prevents interference with other previously installed Python packages.
```
conda create -n npsam python=3.10
conda activate npsam
```

Mandatory: **Install [PyTorch](https://pytorch.org/get-started/locally/) from this link**. NP-SAM has been tested with Pytorch 2.1.2 and CUDA 11.8.

Mandatory: Then install NP-SAM:
```
pip install npsam
```
Optional: Make a static link to the npsam ipykernel (line 2) for easy access to the npsam environment from JupyterLab:
```
python -m ipykernel install --user --name npsam --display-name npsam
```

### Get started
In the npsam environment execute `jupyter lab` in the terminal. This will launch JupyterLab. Try out one of the example notebooks from our GitLab.

## Citation
```
@article{NPSAM,
   author = {Rohde, Rasmus and Villadsen, Torben L. and Mathiesen, Jette K. and Jensen, Kirsten M. Ø and Bøjesen, Espen D.},
   title = {NP-SAM: Implementing the Segment Anything Model for Easy Nanoparticle Segmentation in Electron Microscopy Images},
   journal = {ChemRxiv},
   DOI = {10.26434/chemrxiv-2023-k73qz-v2},
   year = {2023},
   type = {Journal Article}
}
```

## Acknowledgment
This repo benefits from Meta's [Segment Anything](https://github.com/facebookresearch/segment-anything) and [FastSAM](https://github.com/CASIA-IVA-Lab/FastSAM). Thanks for their great work.


