#!/bin/bash
# Run from the root of your repo: bash setup_repo.sh

echo "Creating directory structure..."
mkdir -p data/{raw,processed,external}
mkdir -p notebooks
mkdir -p models/{saved,checkpoints}
mkdir -p src/{data,features,models,utils,visualization}
mkdir -p tests
mkdir -p docs

# Create __init__.py files for all src subpackages
touch src/__init__.py
touch src/data/__init__.py
touch src/features/__init__.py
touch src/models/__init__.py
touch src/utils/__init__.py
touch src/visualization/__init__.py
touch tests/__init__.py

# Create placeholder files so git tracks empty dirs
touch data/raw/.gitkeep
touch data/processed/.gitkeep
touch data/external/.gitkeep
touch models/saved/.gitkeep
touch models/checkpoints/.gitkeep
touch docs/.gitkeep

echo "Directory structure created."
echo "Now create the remaining files listed in the artifact comments, or copy them from the other artifacts."