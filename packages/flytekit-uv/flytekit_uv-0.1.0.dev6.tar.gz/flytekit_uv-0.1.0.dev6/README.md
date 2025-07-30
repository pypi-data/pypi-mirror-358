`flytekit-uv` is a `flytekit` plugin providing an alternative backend for ImageSpec based on [uv](https://docs.astral.sh/uv/), removing the dependency on `micromamba`.

# Installation

```bash
pip install flytekit-uv
```
or equivalent for other Python package managers.

# Usage

```python
from flytekit import ImageSpec

image_spec = ImageSpec(
    builder="uv",
    packages=["pandas"],
)

@task(container_image=image_spec)
def task1():
    import pandas
    ...
```

# Development

Install [uv](https://docs.astral.sh/uv/)
```shell
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Install pre-commit hooks:
```shell
uv run pre-commit install
```