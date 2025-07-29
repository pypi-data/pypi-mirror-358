# NameTrace

``NameTrace`` is a python package to identify "real" human names and predict gender and geographical origin of the name. The idea is to allow users to e.g. take users' names on social media platforms such as X and identify real names and predict gender and possible origin of the users. This package was build to help researchers.

## Features

- **Human Name Detection**: Distinguish between human names and other text (usernames, company names, etc.)
- **Gender Prediction**: Predict gender from names using deep learning models
- **Geographic Origin**: Predict geographic subregion from names
- **High Performance**: Uses BiLSTM neural networks with rule-based fallbacks
- **Easy to Use**: Simple API with batch processing support

## Installation

```bash
pip install nametrace
```

## Quick Start

```python
from nametrace import NameTracer

# Initialize the predictor
nt = NameTracer()

# Predict for a single name
result = nt.predict("John Smith")
print(result)
# {
#   'is_human': True,
#   'gender': 'male',
#   'subregion': 'Northern Europe',
#   'confidence': {
#     'human': 1.0,
#     'gender': 0.9563450217247009,
#     'subregion': 0.40897873044013977
#     }
# }

# Allows batch prediction
names = ["Maria Garcia", "user123", "Ahmed Hassan"]
results = nt.predict(names,batch_size=12)
for name, result in zip(names, results):
    print(f"{name}: {result['is_human']}")

# Maria Garcia: True
# user123: False
# Ahmed Hassan: True


# Allows top k prediction 
result = nt.predict("John Smith",topk=3)
# {
#   'is_human': True,
#   'gender': [
#     ('male', 0.9563450217247009),
#     ('female', 0.04365495219826698)],
#    'subregion': [
#     ('Northern Europe', 0.40897873044013977),
#     ('North America', 0.32769879698753357),
#     ('Australia and New Zealand', 0.16957755386829376)
#     ], 
#   'confidence': {
#     'human': 1.0,
#     'gender': 0.9563450217247009,
#     'subregion': 0.40897873044013977
#     }
# }
```

## API Reference

### NameTracer

The main class for name prediction.

#### `__init__(device=None)`
Initialize the tracer.

**Parameters:**
- `device` (str, optional): Device for model inference ('cpu', 'cuda', or None for auto-detection)

#### `predict(names, batch_size=None, topk=1)`

Predict if a name(s) is(are) human and get demographics.

**Parameters:**
- `names` (str or list): Input name string or list of name strings
- `topk` (int, optional): Provide `topk` predcitions, optional, defaults to 1
- `batch_size` (int, optional): batch size for batch inference, defaults to None (i.e. single batch)

**Returns:**
If `names` is a single name:
- `dict`: Prediction results with keys:
  - `is_human` (bool): Whether the name is human
  - `gender` (str): Predicted gender ('male'/'female') or None
  - `subregion` (str): Predicted geographic subregion or None
  - `confidence` (dict): Confidence scores for each prediction

If `names` is a list of names list of above dict.


## Training Details

NameTrace uses a two-stage approach:

1. **Human Detection**: Rule-based lookup against known name databases, with `BiLSTM` fallback for unknown names
2. **Demographics Prediction**: Character-level `BiLSTM` model for joint gender and geographic origin prediction

## Performance on test data

- **Human Detection**: Acc: 74.46; F1: 76.49
- **Gender Prediction**: Acc: 95.57; Macro F1: 93.01
- **Geographic Origin**: Acc: 66.55; Macro F1: 44.83

## Requirements

- Python 3.9+
- PyTorch 2.0+
- nameparser

## Data and credits
This package was built to allow gender and geographic origin precition in a simple modern api. As such it heavily benefitted from previous work of other authors and packages:

- [name2nat](https://github.com/Kyubyong/name2nat/) (Kyubyong Park, 2020). I built on the data for nationalities collected by Kyubyong Park and convert these to geographic regions. I also extend his dataset by collecting the gender of the names in the dataset from Wikipedia.
- [gender_guesser](https://github.com/lead-ratings/gender-guesser/) (ByRatings, 2016). I take a list of first names from this package, which is originally taken from a ``c`` package by [Jörg Michael (2008)](https://raw.githubusercontent.com/lead-ratings/gender-guesser/refs/heads/master/gender_guesser/data/nam_dict.txt).
- [Gender By Name](https://www.kaggle.com/datasets/rupindersinghrana/gender-by-name) (Rupinder Singh Rana, 2024), which also contains a list of first namnes that I use for training of the human name detection.

## License

GNUv3 License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 