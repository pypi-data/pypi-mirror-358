# Publishing

This module is published to Pypi for use by Python applications.

## Build the Module

Ensure you've bumped the version in pyproject.toml accordingly.

```
uv build
```

## Publish the Module to TestPyPi (Testing, etc)

Prereq: `UV_PUBLISH_TOKEN` must be set

```
uv publish --index testpypi
```

## Publish the Module to PyPi

Prereq: `UV_PUBLISH_TOKEN` must be set

```
uv publish
```
