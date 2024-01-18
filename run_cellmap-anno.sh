#!/bin/bash

echo -e "\n------------------------------------------------------------------------------------"
echo "--------------------------------------CELLMAP---------------------------------------"
echo "------------------------------------------------------------------------------------"

echo -e "\nThis script is intended for a basic execution of the CellMap pipeline."

echo -e "\nFor a complete customizable experience, exit this script and run ./custom_cellmap_setup.sh\n"

echo "The script will perform the following processes:"
echo -e "\t - Create and activate a CellMap-specific conda environment"
echo -e "\t - Import required pipeline modules"
echo -e "\t - Allow the user to configure the pipeline with various parameters"
echo -e "\t - Execute the full CellMap pipeline which will:"
echo -e "\t\t - Resample the provided data"
echo -e "\t\t - Align the data channels with the reference atlas"
echo -e "\t\t - Detect, filter, align and annotate cells"
echo -e "\t\t - Perform voxelization and cell density analysis"
echo -e "\t\t - Export all results to the provided experimental directory\n"

echo "Useful links:"
echo -e "\t - ClearMap2 Source Code - github.com/ChristophKirst/ClearMap2/"
echo -e "\t - ClearMap2 Documentation - christophkirst.github.io/ClearMap2Documentation/"
echo -e "\t - ClearMap Tutorial [VIDEO] - https://youtu.be/-WehURPyIa8\n"

echo "VERIFY BEFORE RUNNING THE PIPELINE:"
echo -e "\t - Experimental directory contains only two folders (for raw and autof data)"
echo -e "\t - Experimental directory is in an LSS drive or other large storage disk"
echo -e "\t\t - CellMap can write 100+ GB of data to your experimental directory"
echo -e "\t - Experimental data is cropped to remove excess empty space\n"

read -r -p "Would you like to proceed with the CellMap pipeline? ([y]/n): " response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]
then
    echo -e "\nInitializing pipeline..."
else
    echo -e "\nExiting script...\n"
    exit 0
fi

eval "$(conda shell.bash hook)" # for activating conda environments
echo -e "\nChecking for environment...\n"

conda env list | grep -q "ClearMapHPC"
if [ $? -eq 0 ]; then
    echo "The conda environment \"ClearMapHPC\" already exists."
    echo "Activating ClearMapHPC..."
    conda activate ClearMapHPC
    echo "ClearMapHPC successfully activated!"
else
    echo "The conda environment \"ClearMapHPC\" is not installed."
    echo -e "\nThe CellMap pipeline can only proceed within the proper environment"
    read -r -p "Would you like to install it? ([y]/n): " response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]
    then
        echo -e "Creating conda environment from ClearMapHPC.yml..."
        echo "(This may take a few minutes)"
        conda env create -f ClearMapHPC.yml -y
        echo "Environment successfully installed!"
        echo "Activating ClearMapHPC..."
        conda activate ClearMapHPC
        echo -e "ClearMapHPC successfully activated!"
    else
        echo -e "\nExiting script..."
        exit 0
    fi
fi

echo -e "\nBefore executing the CellMap script, verify that config_parameters.yml contains your desired experimental parameters!"

CLEARMAP_PATH=$(pwd) # Set ClearMap path to current path

echo -e "\nWould you like to begin executing CellMap ([y]/n)?"
read INPUT
if [[ "$INPUT" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    cd
    cd $CLEARMAP_PATH
    python ClearMap/Scripts/CellMap-anno.py "$CLEARMAP_PATH"
else
    echo -e "\nExiting script...\n"
    exit 0
fi
