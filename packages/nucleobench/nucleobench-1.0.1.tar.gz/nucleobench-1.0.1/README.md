# NucleoBench

This is the initial repo for an upcoming paper, `NucleoBench: A Large-Scale Benchmark of Neural Nucleic Acid Design Algorithms`.

This repo is covered by the Apache-2.0 license.

This repo is intended to be used in a few ways:

1. Reproducing the results from our paper.
1. Running the NucleoBench sequence designers on custom problems.
1. Using our new designer, AdaBeam, on a custom problem.

To do these, you can clone this repo, use the Docker image (for the benchmark), or use the PyPi package for our designers.

## Results

![Summary of results.](https://raw.githubusercontent.com/move37-labs/nucleobench/main/assets/images/results_summary.png)

## Installation from PyPi

```bash
pip install nucleobench  # optimizers and tasks
pip install nucleopt  # smaller, faster install for just optimizers
```

Then you can use it in python:
```python
from nucleobench import optimizations
opt = optimizations.get_optimization('beam_search_unordered')  # Any optimizer name.
```

## Installation & testing from GitHub

```bash
# Clone the repo.
git clone https://github.com/move37-labs/nucleobench.git
cd nucleobench

# Create and activate the conda environment.
conda env create -f environment.yml
conda activate nucleobench

# Run all the unittests.
pytest nucleobench/
```

You can also run the integration tests, which require an internet connection:

```bash
pytest docker_entrypoint_test.py
```

## Running NucleoBench from PyPi or Docker

See the `recipes/colab` folder for examples of how to run the designers with PyPi.
See the `recipes/docker` folder for examples of how to run the designers with Docker.
See the `recipes/python` folder for examples of how to run the designers with the cloned github repo.

## Building a Docker image

To help deploy NucleoBench to the cloud, we've created a docker container. To build it yourself, see the top of `Dockerfile` for instructions. One way of creating a docker file is:

```bash
docker build -t nucleobench -f Dockerfile .
```