#!/bin/bash

read -p "Do you wish to run CellMap ([y]/n)?" answer
case ${answer:0:1} in
    y|Y )
    ;;
    * )
        exit
    ;;
esac 

echo "Configuring CellMap..."

# Get ClearMap2 path 
sysappendpath=$(pwd)

echo $sysappendpath

# Get experimental directory path

read -p "Enter experimental directory path (/path/to/directory/): " directory_path

echo $directory_path

# Get path to raw and autof data

read -p "Enter location to the raw expression data (raw_folder/raw_data_Z<Z,4>.tif): " raw_data

echo $raw_data

read -p "Enter location to the autoflorescent expression data (autof_folder/autof_data_Z<Z,4>.tif): " autof_data

echo $autof_data

# Slice and orient Data

# Obtain data resolution

# Set cell detection parameters

# Set processing parameters

# Set cell filtration parameters

# Set cell filtration thresholds

# conda env create -f ClearMapUi39.yml
# conda env create -n bashenv python=3.9 -y
# conda activate bashenv
