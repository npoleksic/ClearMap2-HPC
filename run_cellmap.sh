#!/bin/bash

echo -e "\n------------------------------------------------------------------------------------"
echo "--------------------------------------CELLMAP---------------------------------------"
echo "------------------------------------------------------------------------------------"
echo -e "\nThis script is intended for a basic execution of the CellMap pipeline."
echo -e "\nThe script will perform the following processes:"
echo -e "\t - Create and activate a conda environment necessary for executing CellMap"
echo -e "\t - Import required pipeline modules"
echo -e "\t - Allow the user to configure the pipeline with various parameters"
echo -e "\t - Execute the full CellMap pipeline which will:"
echo -e "\t\t - Resample the provided data"
echo -e "\t\t - Align the data to the reference atlas"
echo -e "\t\t - Detect, filter, align and annotate cells"
echo -e "\t\t - Perform voxelization and cell density analysis"
echo -e "\t\t - Export all results to the provided experimental directory"

echo -e "\nFor a more customizable experience, exit this script and run /.custom_cellmap_setup.sh"

echo -e "Would you like to begin executing the CellMap pipeline? ([y]/n)"

conda env create -f ClearMapHPC.yml -y
conda activate ClearMapHPC