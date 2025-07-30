# Syndrilla
A PyTorch-based numerical simulator for decoders in quantum error correction.

## Installation
Before installation, git clone this GitHub [repo](https://github.com/UNARY-Lab/syndrilla).

### Option 1: pip installation (python>=3.9)
In the root directory of the repo, run following commands.
1. ```conda create --name syndrilla python```
2. ```conda activate syndrilla```
3. ```pip install syndrilla```
4. ```syndrilla -h``` to validate installation
5. You can run ```syndrilla``` in *any* directory.

### Option 2: source installation
In the root directory of the repo, run following commands.
1. ```conda create --name syndrilla python```
2. ```conda activate syndrilla```
3. ```conda install -c conda-forge pyyaml yamlordereddictloader pytest loguru numpy scipy pyfiglet pynvml```
4. Install [PyTorch 2.x](https://pytorch.org/)
5. ```python3 -m pip install -e . --no-deps```
6. ```pytest``` to validate installation
7. You can *only* run ```syndrilla``` in root directory.

### Option 3: verifiable installation (with restricted python version)
In the root directory of the repo, run following commands.
1. ```conda create --name syndrilla python=3.10```
2. ```conda activate syndrilla```
3. ```conda install -c conda-forge pyyaml yamlordereddictloader pytest loguru numpy scipy pyfiglet pynvml```
4. Install [PyTorch 2.x](https://pytorch.org/)
5. ```python3 -m pip install -e . --no-deps```
6. ```pytest``` to validate installation
7. ```pip install -U bposd``` to install BPOSD
8. ```python tests/validate_bposd.py``` to validate against [BPOSD](https://github.com/quantumgizmos/bp_osd)
9. You can *only* run ```syndrilla``` in root directory.

