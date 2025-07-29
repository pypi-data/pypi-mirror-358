# Ansible Env Vars
[![Nox](https://github.com/level12/ans-env-loader/actions/workflows/nox.yaml/badge.svg)](https://github.com/level12/ans-env-loader/actions/workflows/nox.yaml)
[![pypi](https://img.shields.io/pypi/v/ans-env-loader)](https://pypi.org/project/ans-env-loader/)

Extracts variables from the local environment and converts them to Ansible variables.

## Install and Setup

Install: `uv add [--dev] ans-env-loader`

Then place an `ans-env-vars.yaml` and an `env-loader.py` into your Ansible playbooks root directory
as follows:

```sh
 ❯ tree
├── ansible.cfg
├── ans-env-vars.yaml
├── hosts.ini
├── playbook.yaml
└── vars_plugins
    ├── env-loader.py


 ❯ cat vars_plugins/env-loader.py
from ans_env_loader import VarsModule as VarsModule


 ❯ cat ans-env-vars.yaml
# Ansible var name is the same as the expected env var
- app_smtp_host
# Map Ansible var name to a different expected env var
- app_flask_secret: FLASK_SECRET
```

## Dev

### Copier Template

Project structure and tooling mostly derives from the [Coppy](https://github.com/level12/coppy),
see its documentation for context and additional instructions.

This project can be updated from the upstream repo, see
[Updating a Project](https://github.com/level12/coppy?tab=readme-ov-file#updating-a-project).

### Project Setup

From zero to hero (passing tests that is):

1. Ensure [host dependencies](https://github.com/level12/coppy/wiki/Mise) are installed

2. Start docker service dependencies (if applicable):

   `docker compose up -d`

3. Sync [project](https://docs.astral.sh/uv/concepts/projects/) virtualenv w/ lock file:

   `uv sync`

4. Configure pre-commit:

   `pre-commit install`

5. Run tests:

   `nox`

### Versions

Versions are date based.  A `bump` action exists to help manage versions:

```shell

  # Show current version
  mise bump --show

  # Bump version based on date, tag, and push:
  mise bump

  # See other options
  mise bump -- --help
```
