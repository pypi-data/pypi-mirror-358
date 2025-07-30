# Dubidoc API client ✍

[![PyPI](https://img.shields.io/pypi/v/dubidoc?style=flat-square)](https://pypi.python.org/pypi/dubidoc/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dubidoc?style=flat-square)](https://pypi.python.org/pypi/dubidoc/)
[![PyPI - License](https://img.shields.io/pypi/l/dubidoc?style=flat-square)](https://pypi.python.org/pypi/dubidoc/)

---
**Documentation**: [https://my.dubidoc.com.ua/api/api/v1/docs](https://my.dubidoc.com.ua/api/api/v1/docs)

**Source Code**: [https://github.com/DmytroLitvinov/python-dubidoc](https://github.com/DmytroLitvinov/python-dubidoc)

**PyPI**: [https://pypi.org/project/dubidoc/](https://pypi.org/project/dubidoc/)

---

Python API wrapper around Dubidoc API. Feel free to contribute and make it better! 🚀

**NOTE**: Since it is early release, some of the API endpoints may not be implemented yet. If you need some specific endpoint, feel free to create an issue or pull request.
Also, library can be changed in the future, so be careful with the updates as for now.

## Installation

```sh
pip install dubidoc
```

## Usage

1) Request your token at [Dubidoc team](https://t.me/dmytro_dubilet/814)

2) Use that token to initialize client:

```python
from dubidoc import DubidocAPIClient

api_token = 'xxxxxxxxxxxxxxx'

dubidoc = DubidocAPIClient(api_token)

documents = dubidoc.document_api.list()
print(documents.data, documents.response_code)
```

## License

This project is licensed under the terms of the [MIT license](https://github.com/DmytroLitvinov/python-dubidoc/blob/master/LICENSE).


### HOW TO MAKE A RELEASE

* Add changes to `CHANGELOG.md`
* Change version in `dubidoc/__init__.py` and `pyproject.toml`
* `source .env/bin/activate`
* `python3 -m build --sdist --wheel`
* `twine upload dist/*`
