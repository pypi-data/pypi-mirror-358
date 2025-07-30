# esbm-dis-dfts-pyeqx-core

Spark: `3.5.3`

## pre-requisites

to setup virtual environment to execute unit tests, it has to setup virtual env and install dependencies

```bash
# setup virtual env
python3.12 -m venv .venv

# activate virtual env
source .venv/bin/activate

# install dependencies
pip install delta-spark pyspark pandas retrying minio requests

# install dependencies (If you want to publish)
pip install twine
```

## tests

to execute unit test run this command at root of the project

```bash
python3 -m unittest discover test -p "**.py"

# or

pytest
```

## build

```bash
python3 -m pip install --upgrade build
python3 -m build
```

## publish to testpypi

```bash
python3 -m twine upload --repository testpypi dist/*
```

## publish to pypi

```bash
python3 -m twine upload dist/*

# specific config for pypi
python3 -m twine upload --config-file .pypirc dist/*
```

## publish to gitlab

```bash
python3 -m twine upload --repository-url https://gitlab.com/api/v4/projects/<project_id>/packages/pypi/ --username gitlab-ci-token --password <access_token> dist/*

# Replace <project_id> with the ID of your GitLab project
```

## install from gitlab

```bash
#install from pypi
pip install pyeqx-core

#install from testpypi
pip install -i https://test.pypi.org/simple/ pyeqx-core

# install from gitlab
pip install datadriven-core --index-url https://__token__:<access_token>@gitlab.com/api/v4/projects/<project_id>/packages/pypi/simple
pip install pyeqx-core --index-url https://__token__:<access_token>@gitlab.com/api/v4/projects/<project_id>/packages/pypi/simple
# Replace <project_id> with the ID of your GitLab project
```
