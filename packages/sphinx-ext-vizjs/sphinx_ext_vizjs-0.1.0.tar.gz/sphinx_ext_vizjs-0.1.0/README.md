sphinx-ext-vizjs
----------------

Install:

```bash
pip install sphinx-ext-vizjs
```

Add to your `conf.py`:

```python
extensions = [
    "sphinx_ext_vizjs",
    ...
]
```

Use in your rst:

```rst
.. vizjs::

   digraph {
     a -> b
   }
```
