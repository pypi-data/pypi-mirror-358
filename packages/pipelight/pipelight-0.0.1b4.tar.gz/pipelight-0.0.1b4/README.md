# Pipelight: The Easiest Pipeline for Training, Validation and Test Based on PyTorch Lightning

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/Python-3.7%2B-green)](https://www.python.org/)
[![PyTorch Version](https://img.shields.io/badge/PyTorch-2.0%2B-orange)](https://pytorch.org/)
[![PyTorch Lightning Version](https://img.shields.io/badge/PyTorch_Lightning-2.4.0%2B-blue)](https://lightning.ai/pytorch-lightning)

**Pipelight** is a pipeline that is driven by configuration files for model running based on PyTorch Lightning.

## Key Features
- **Reproducible Pipelines**: Built-in experiment tracking and deterministic training
- **Configuration-Driven Workflows**: Define experiments through YAML configs with PyTorch Lightning integration

## Installation
```bash
pip install pipelight
```

## Quick Start

### Configuration-Based Execution
Copy `pipelight/configs` as a template to the project folder, and enter this folder. All YAML files can be modified to meet the task requirements.

For training and validation, just run:
```bash
python -m pipelight.run --train configs/train.yaml --val configs/val.yaml -m {model config} -r configs/running/runner.yaml -n experiment_01
```

After that, run the following to test:
```bash
python -m pipelight.run --test configs/test.yaml -m {model config} -r configs/running/runner.yaml -n experiment_01
```
Make sure the name of the experiment should be kept the same.