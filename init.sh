#!/bin/bash
set -euxo pipefail

trap 'echo "ERROR: init.sh failed at line $LINENO"' ERR

cd /home/onyxia/work

echo "USER=$(whoami)"
echo "HOME=$HOME"
echo "PWD=$(pwd)"

### === Install Miniforge (user-local) ===
MINIFORGE=Miniforge3-Linux-x86_64.sh
INSTALL_DIR=$HOME/miniforge3

echo "🔧 Installing Miniforge..."
wget https://github.com/conda-forge/miniforge/releases/latest/download/$MINIFORGE -O $MINIFORGE
bash $MINIFORGE -b -p $INSTALL_DIR
rm $MINIFORGE

# Enable conda commands in this shell
source $INSTALL_DIR/etc/profile.d/conda.sh

### === Create and activate environment ===
echo "🧪 Creating conda environment 'foccus_storm_surge_demonstrator'..."
conda create -y -n foccus_storm_surge_demonstrator python=3.10.9
conda activate foccus_storm_surge_demonstrator


conda install -y -c conda-forge
# Install mamba
# conda install -y -c conda-forge mamba

# ### === Install exact packages ===
# echo "📦 Installing required packages..."
# mamba install -y -c conda-forge \
#   folium==0.20.0 \
#   matplotlib==3.10.9 \
#   numpy==2.2.6 \
#   pandas==2.3.3 \
#   netcdf4==1.7.4 \
#   pyproj==3.7.1 \
#   ipywidgets==8.1.8 \
#   plotly==6.9.0 \
#   xarray==2025.6.1 \
#   pyyaml==6.0.3 \
#   contextily==1.7.1 \
#   pymupdf \
#   s3fs \
#   ipykernel jupyterlab nbformat nbconvert

### === Register kernel for Jupyter ===
echo "🔗 Registering Jupyter kernel..."
python -m ipykernel install --user --name foccus_storm_surge_demonstrator --display-name "Python (foccus_storm_surge_demonstrator)"

### === Clone repo and install local package ===
echo "📥 Cloning FOCCUS_demonstrator repo..."
REPO_DIR=FOCCUS_demonstrator
BRANCH_NAME=main
git clone --branch "$BRANCH_NAME" --single-branch https://github.com/CoLAB-ATLANTIC/FOCCUS_demonstrator.git "$REPO_DIR"
cd "$REPO_DIR"

python -m pip install -r requirements.txt

mv notebooks/FOCCUS_D8_1_Demonstrator.ipynb notebooks/main.ipynb

echo "📦 Installing local 'demonstrator' package (editable)..."
pip install -e .

NOTEBOOK=notebooks/main.ipynb

### === Embed kernel metadata ===
echo "⚙️ Embedding kernel metadata into notebook..."
python - <<EOF
import nbformat

nb_path = "$NOTEBOOK"
nb = nbformat.read(open(nb_path), as_version=nbformat.NO_CONVERT)

nb["metadata"]["kernelspec"] = {
    "name": "demonstrator",
    "display_name": "Python (demonstrator)",
    "language": "python"
}

nbformat.write(nb, open(nb_path, "w"))
EOF

### === Clear notebook output ===
echo "🧼 Clearing cell outputs..."
jupyter nbconvert --clear-output --inplace "$NOTEBOOK"

echo "✅ Setup complete. You can now open $REPO_DIR/$NOTEBOOK and it will use the 'foccus_storm_surge_demonstrator' kernel by default."

rm init.sh