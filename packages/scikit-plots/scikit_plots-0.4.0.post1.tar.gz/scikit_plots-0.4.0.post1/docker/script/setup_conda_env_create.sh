#!/bin/bash

# Copied scipy project

set -e

"${SHELL}" <(curl -Ls micro.mamba.pm/install.sh) < /dev/null

conda init --all
micromamba shell init -s bash
micromamba env create -f environment.yml --yes
# Note that `micromamba activate scipy-dev` doesn't work, it must be run by the
# user (same applies to `conda activate`)

# Enables users to activate environment without having to specify the full path
echo "envs_dirs:
  - /home/codespace/micromamba/envs" > /opt/conda/.condarc

pip cache purge || true
rm -rf ~/.cache/* || true
sudo apt-get clean || true
