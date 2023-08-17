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

echo "Helpful links:"
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
        echo -e "ClearMapHPC successfully activated!\n"
    else
        echo -e "\nExiting script...\n"
        exit 0
    fi
fi

## MANDATORY PARAMETERS
CLEARMAP_PATH = $(pwd)
DATA_DIR = "NULL"
RAW_DATA_PATH = "NULL"
AUTOF_DATA_PATH = "NULL"
RAW_DATA_RES = "NULL"
AUTOF_DATA_RES = "NULL"
SYSTEM_VERBOSITY = "NULL" # Make optional/provide default value

## ATLAS CONFIGURATION
ATLAS_ORIENTATION = "NULL" # Provide instructions 
ATLAS_X_CROP = "NULL" 
ATLAS_Y_CROP = "NULL"
ATLAS_Z_CROP = "NULL"

## CELL DETECTION PARAMETER CONFIGURATION
# ILLUMINATION CORRECTION
ILLUMINATION_FLATFIELD = "NULL"
ILLUMINATION_BACKGROUND = "NULL"
ILLUMINATION_SCALING = "NULL"
ILLUMINATION_SAVE = "NULL"
# BACKGROUND REMOVAL
BACKGROUND_SHAPE = "NULL"
BACKGROUND_FORM = "NULL"
BACKGROUND_SAVE = "NULL"
# EQUALIZATION
EQ_PERCENTILE = "NULL"
EQ_MAX = "NULL"
EQ_SELEM = "NULL"
EQ_SPACING = "NULL"
EQ_INTERPOLATE = "NULL"
EQ_SAVE = "NULL"
# DoG FILTER
DOG_SHAPE = "NULL"
DOG_SIGMA = "NULL"
DOG_SIGMA2 = "NULL"
DOG_SAVE = "NULL"
# MAXIMA DETECTION
MAXIMA_HMAX = "NULL"
MAXIMA_SHAPE = "NULL"
MAXIMA_THRESHOLD = "NULL"
MAXIMA_SAVE = "NULL"
# SHAPE DETECTION
SHAPE_THRESHOLD = "NULL"
SHAPE_SAVE = "NULL"
# INTENSITY DETECTION
INTENSITY_METHOD = "NULL"
INTENSITY_SHAPE = "NULL"
INTENSITY_MEASURE = "NULL"
INTENSITY_SAVE = "NULL"

## SYSTEM PROCESSING CONFIGURATION ((consider setting by default))
PROC_MAX = "NULL"
PROC_MIN = "NULL"
PROC_OVERLAP = "NULL"
PROC_AXES = "NULL"
PROC_OPTIMIZE = "NULL"
PROC_OPTIMIZE_FIX = "NULL"

## POST-PROCESSING CONFIGURATION
# CELL FILTRATION
FILTER_THRESHOLD = "NULL" # Potentially multiple
# ANNOTATION
ANNOTATE_NAME = "NULL" # Consider requiring by default
ANNOTATE_ID = "NULL" 
ANNOTATE_ACRONYM = "NULL"
ANNOTATE_PARENT = "NULL"
ANNOTATE_ATLAS = "NULL"
ANNOTATE_ONTOLOGY = "NULL"
ANNOTATE_COLOR = "NULL"
ANNOTATE_STLVL = "NULL"
ANNOTATE_HEMISPHERE = "NULL"
# VOXELIZATION
VOXEL_WEIGHT = "NULL"
VOXEL_METHOD = "NULL"
VOXEL_RADIUS = "NULL"
VOXEL_KERNEL = "NULL"

echo -e "\nSUCCESS\n"


