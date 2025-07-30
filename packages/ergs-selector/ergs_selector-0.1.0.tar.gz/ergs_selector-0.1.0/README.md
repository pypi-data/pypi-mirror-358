# ERGS Selector

`ergs-selector` is a Python package for performing Effective Range-based Feature Selection (ERGS) for classification problems. It helps select features based on their value range separation across classes.

## Installation

```bash
pip install ergs-selector
```

## Usage

```python
from ergs_selector import ERGSSelector

selector = ERGSSelector(top_k=15)
X_selected = selector.fit_transform(X, y)
```

## License

MIT
