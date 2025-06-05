# django-nifty-layout

[![PyPI Version](https://img.shields.io/pypi/v/nifty_layout.svg)](https://pypi.python.org/pypi/django-nifty-layout) ![Test with tox](https://github.com/powderflask/django-nifty-layout/actions/workflows/tox.yaml/badge.svg) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/powderflask/django-nifty-layout)

Version: 0.1.1

A simple but flexible layout tool for composing and transforming data for structured template components.
Inspired by `crispy-forms` Layout, but without the forms.

django-nifty-layout is free software distributed under the MIT License.


## Quick Start

1. Install the `django-nifty-layout` package from PyPI
    ```bash
    $ pip install django-nifty-layout
    ```

2. Go grab a drink, you are all done!
   

## Sample Usage
layout.py
```
from django.utils.formats import date_format

from nifty_layout.components import (
   DictCompositeNode as Dct,
   FieldNode as Fld,   
   Seq,
)

# ----- Safe Date Formatter ----- #
date_formatter = lambda val: None if val is None else date_format(val, SHORT_DATE_FORMAT)

layout = Dct(
    dict(
        overview=Seq(
             "title",
             Fld("date", formatter=date_formatter),
             report_type",
             "location",
             labeller="Overview",
        ),
        contacts=Seq(
            Dct(dict(
                    name="contact_name",
                    contact_methods=Seq("contact_email"),
                ), labeller="Primary Contact"
            ),
            Dct(dict(
                    name="reported_by_name",
                    contact_methods=Seq("reported_by_phone_num", "reported_by_email"),
                 ), labeller="Reported By"
            ),
            labeller="Contacts",
        ),
        ...
    )
)
```

views.py
```
def report_view(request, pk):
   ...
   obj = Report.objects.get(pk=pk)
   ...
   return render(request, "template.html", dict(report=layout.bind(obj)))
```

template.html
```
...
<div class="report>
  <h2>report.overview.label</h2>
  {% for node in report.overview %}
      <div class="row">
         <div class="col label">{{ node.label }}</div>
         <div class="col value">{{ node.value|default:"" }}</div>
      {% endfor %}
      </div>
  {% endfor %}
  <div class="row">
    {% for contact in report.contacts %}
      <div class="col">
        {% include "contact_card.html" %}
      </div>
    {% endfor %}
  </div>
   ...
</div>   
```

## Get Me Some of That
* [Source Code](https://github.com/powderflask/django-nifty-layout)

* [Issues](https://github.com/powderflask/django-nifty-layout/issues)
* [PyPI](https://pypi.org/project/django-nifty-layout)

[MIT License](https://github.com/powderflask/django-nifty-layout/blob/master/LICENSE)

### Check Out the Demo App

1. `pip install -e git+https://github.com/powderflask/django-nifty-layout.git#egg=django-nifty-layout`
1. `inv demo.install`  ** coming soon **
1. `python demo_app/manage.py runserver`

See [demo_app/README](demo_app/README.md)

### Acknowledgments
This project would be impossible to maintain without the help of our generous [contributors](https://github.com/powderflask/django-nifty-layout/graphs/contributors)

#### Technology Colophon

Without django and the django dev team, the universe would have fewer rainbows and ponies.

This package was originally created with [`cookiecutter`](https://www.cookiecutter.io/) 
and the [`cookiecutter-powder-pypackage`](https://github.com/JacobTumak/CookiePowder) project template.


## For Developers
Install `invoke`, `pip-tools`, `tox` for all the CLI goodness
  ```bash
   pip install invoke pip-tools tox
   ```

Initialise the development environment using the invoke task
   ```bash
   inv tox.venv
   ```
Or create it with tox directly
   ```bash
   tox d -e dev .venv
   ```
Or build and install the dev requirements with pip
   ```bash
   inv deps.compile-dev
   pip install -r requirements_dev.txt
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
