# Trolskgen

# Hello World

After `pip install trolskgen`, just run:

# TODO

- README
    - Walk through each converter
    - Plugins example
- Implement comments somehow? Monkeypatch ast?
- Notes on comments - use docstrings etc.

# Development

```
uv pip install -e '.[dev]'
mypy .
pytest -vv
uv pip install build twine
python -m build
twine check dist/*
twine upload dist/*
```
