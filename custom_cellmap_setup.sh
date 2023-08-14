conda env create -f ClearMapHPC.yml -y
conda activate ClearMapHPC
python -m ipykernel install --user --name ClearMapHPC --display-name “ClearMapHPC”