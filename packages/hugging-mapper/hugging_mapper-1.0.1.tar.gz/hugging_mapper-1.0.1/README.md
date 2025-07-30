![img](https://raw.githubusercontent.com/angelphanth/hugging-mapper/refs/heads/main/docs/assets/hugger-logo-wide.svg)

<h1 align="center">Hugging-Mapper</h1>
<p align="center"><em>A lightweight python tool for easy text similarity scoring using Hugging Face models</em></p>

<p align="center">
    <a href="https://pypi.org/project/hugging-mapper/">
        <img src="https://img.shields.io/pypi/v/hugging-mapper?label=PyPI" alt="PyPI">
    </a>
    <a href="https://github.com/angelphanth/hugging-mapper/actions/workflows/cicd.yml">
        <img src="https://github.com/angelphanth/hugging-mapper/actions/workflows/cicd.yml/badge.svg?branch=" alt="Python application">
    </a>
    <a href="https://hugging-mapper.readthedocs.io/en/latest/?badge=latest">
        <img src="https://readthedocs.org/projects/hugging-mapper/badge/?version=latest" alt="Read the Docs">
    </a>
    <img src="https://img.shields.io/pypi/pyversions/hugging-mapper" alt="PyPI - Python Version">
    <br>
    <br>
    <img src="https://img.shields.io/github/issues/angelphanth/hugging-mapper" alt="GitHub issues">
    <img src="https://img.shields.io/github/license/angelphanth/hugging-mapper" alt="GitHub license">
    <img src="https://img.shields.io/github/last-commit/angelphanth/hugging-mapper" alt="GitHub last commit">
    <img src="https://img.shields.io/github/stars/angelphanth/hugging-mapper?style=social" alt="GitHub stars">
</p>


## Table of Contents :bookmark_tabs:

- [Installation](#installation)
- [Features](#features)
- [Usage](#usage)
- [Documentation](#documentation)
- [License](#license)

## Installation 

```bash
pip install hugging-mapper
```

## Features
- Easily compare how similar two pieces of text are
- Customizable model selection at initialization
- Works with Hugging Face models that create sentence embeddings
- Batch scoring for lists of sentence pairs


## Usage

Embedding text using huggingface models
```python
from hugger.mapper import HuggingMapper

# init
# default model_name is 'cambridgeltl/SapBERT-from-PubMedBERT-fulltext'
mapper = HuggingMapper(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# generate embedding
embedding = mapper.embed_text("I hope you'll find this helpful.")
```

Similarity search of given data
```python
from hugger.mapper import NodeMapper
import pandas as pd

# demo data
data = pd.DataFrame({
    "id": ["node1", "node2", "node3"], 
    "text": ["Disease", "Gene", "Drug"]
})

# generate embeddings for data using (default) huggingface model
node_mapper = NodeMapper(data)

# get most similar 
# threshold 0 returns all data sorted by similarity to the given term
most_similar = node_mapper.get_similar("protein", threshold=0)

# get matching node
node_id, metadata = node_mapper.get_match("genetics", threshold=0.7)
```

## Documentation 

Tutorials and documentation are available on [Read the Docs](https://hugging-mapper.readthedocs.io/) :notebook_with_decorative_cover::grinning:

## License

This project is licensed under the MIT License.