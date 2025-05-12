# django-nifty-layout

[![PyPI Version](https://img.shields.io/pypi/v/nifty_layout.svg)](https://pypi.python.org/pypi/django-nifty-layout) ![Test with tox](https://github.com/powderflask/django-nifty-layout/actions/workflows/tox.yaml/badge.svg) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/powderflask/django-nifty-layout)

Version: 0.1.0

A flexible data composition tool to simplify writing templates.




django-nifty-layout is free software distributed under the MIT License.



## Features

- Feature 1
- Feature 2
- Feature 3


## Quick Start

1. Install the `django-nifty-layout` package from PyPI
    ```bash
    $ pip install django-nifty-layout
    ```

2. Add `'nifty_layout'` to `INSTALLED_APPS`:
    ```python
    INSTALLED_APPS = [
        ...,
        "nifty_layout",
           ...,
    ]
    ```
   
## Get Me Some of That
* [Source Code](https://github.com/powderflask/django-nifty-layout)

* [Issues](https://github.com/powderflask/django-nifty-layout/issues)
* [PyPI](https://pypi.org/project/django-nifty-layout)

[MIT License](https://github.com/powderflask/django-nifty-layout/blob/master/LICENSE)

### Check Out the Demo App

1. `pip install -e git+https://github.com/powderflask/django-nifty-layout.git#egg=django-nifty-layout`
1. `python django-nifty-layout/manage.py install_demo`
1. `python django-nifty-layout/manage.py runserver`


### Acknowledgments
This project would be impossible to maintain without the help of our generous [contributors](https://github.com/powderflask/django-nifty-layout/graphs/contributors)

#### Technology Colophon

Without django and the django dev team, the universe would have fewer rainbows and ponies.

This package was originally created with [`cookiecutter`](https://www.cookiecutter.io/) 
and the [`cookiecutter-powder-pypackage`](https://github.com/JacobTumak/CookiePowder) project template.


## For Developers
Initialise the development environment using the invoke task
   ```bash
   inv tox.venv
   ```
Or create it with tox directly
   ```bash
   tox d -e dev .venv
   ```
Or install the dev requirements with pip
   ```bash
   pip install -r reqirements_dev.txt
   ```

### Tests
   ```bash
   pytest
   ```
or
   ```bash
   tox r
   ```
or run tox environments in parallel using
   ```bash
   tox p
   ```

### Code Style / Linting
   ```bash
   $ isort
   $ black
   $ flake8
   ```

### Versioning
 * [Semantic Versioning](https://semver.org/)
   ```bash
   $ bumpver show
   ```



### Build / Deploy Automation
 * [invoke](https://www.pyinvoke.org/)
   ```bash
   $ invoke -l
   ```
 * [GitHub Actions](https://docs.github.com/en/actions) (see [.github/workflows](https://github.com/powderflask/django-nifty-layout/tree/master/.github/workflows))
 * [GitHub Webhooks](https://docs.github.com/en/webhooks)  (see [settings/hooks](https://github.com/powderflask/django-nifty-layout/settings/hooks))
