# COCO API tools for 🤗 Huggingface Dataset

[![CI](https://github.com/shunk031/huggingface-datasets_cocoapi-tools/actions/workflows/ci.yaml/badge.svg)](https://github.com/shunk031/huggingface-datasets_cocoapi-tools/actions/workflows/ci.yaml)
[![Release](https://github.com/shunk031/huggingface-datasets_cocoapi-tools/actions/workflows/release.yaml/badge.svg)](https://github.com/shunk031/huggingface-datasets_cocoapi-tools/actions/workflows/release.yaml)
[![Deploy](https://github.com/shunk031/huggingface-datasets_cocoapi-tools/actions/workflows/deploy.yaml/badge.svg)](https://github.com/shunk031/huggingface-datasets_cocoapi-tools/actions/workflows/deploy.yaml)
[![Python](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11-blue?logo=python)](https://pypi.python.org/pypi/huggingface-datasets-cocoapi-tools)
[![PyPI](https://img.shields.io/pypi/v/huggingface-datasets-cocoapi-tools.svg)](https://pypi.python.org/pypi/huggingface-datasets-cocoapi-tools)

A helper library for easily converting [MSCOCO format data](https://cocodataset.org/#home) using [the loading script](https://huggingface.co/docs/datasets/dataset_script) of [🤗 huggingface datasets](https://github.com/huggingface/datasets).

## Installation

You can install the library via pip:

```shell
pip install huggingface-datasets-cocoapi-tools
```

You can also install the library with the optional dependencies:

```shell
# for pycocotools
pip install 'huggingface-datasets-cocoapi-tools[cocoapi]' 

# for huggingface/datasets
pip install 'huggingface-datasets-cocoapi-tools[datasets]' 

# for all dependencies
pip install 'huggingface-datasets-cocoapi-tools[all]'
```

## Acknowledgement

- cocodataset/cocoapi: COCO API - Dataset @ http://cocodataset.org/ https://github.com/cocodataset/cocoapi 
- ppwwyyxx/cocoapi: Contains the "pycocotools" package on PyPI. Changes made to the official cocoapi about packaging. https://github.com/ppwwyyxx/cocoapi 
- nightrome/cocostuffapi: COCO Stuff API https://github.com/nightrome/cocostuffapi 
