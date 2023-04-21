#!/bin/bash

# Download Poetry installation script
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -

# Charge les variables d'environnement de Poetry
source $HOME/.poetry/env

# Installe les bibliothèques requises avec Poetry
poetry install
