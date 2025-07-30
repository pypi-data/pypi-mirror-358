# esbm-dis-dfts-pyeqx-common

This project is a common library for pyeqx projects.

## pre-requisites

to setup virtual environment to execute unit tests, it has to setup virtual env and install dependencies

```bash
# setup virtual env
python3.11 -m venv .venv

# activate virtual env
source .venv/bin/activate
```

## tests

to execute unit test run this command at root of the project

```bash
pytest -s
```

## build

to build the package run this command at root of the project

```bash
python3 -m pip install --upgrade build
python3 -m build
```

## extra

To update dependencies, execute below command

```python
pip3 list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1  | xargs -n1 pip3 install -U
```
