#!/bin/bash

function return_bool() {
    local INPUT="$1"
    if [[ "$INPUT" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        echo "True"
    elif [[ "$INPUT" =~ ^([nN][oO]|[nN])$ ]]; then
        echo "False"
    else
        echo "Invalid"
    fi
}
function validate_path() {
    local PATH="$1"
    if [ ! -d "$PATH" ]; then
        echo "INVALID"
    else
        echo "VALID"
    fi
}
function validate_num() {
    local INPUT="$1"  
    if [[ $INPUT =~ ^[0-9]+([.][0-9]*)?$ ]]; then
        echo "VALID"
    else
        echo "INVALID"
    fi
}
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
        echo -e "ClearMapHPC successfully activated!"
    else
        echo -e "\nExiting script..."
        exit 0
    fi
fi

echo -e "\nExperimental Parameter Configuration"

CLEARMAP_PATH=$(pwd) # Set ClearMap path to current path

while true; do
    echo -e "\nEnter the PATH to the experimental data directory: "
    read DATA_PATH
    PATH_CHECK=$(validate_path "$DATA_PATH")
    
    if [ "$PATH_CHECK" == "VALID" ]; then
        cd $DATA_PATH
        DATA_PATH=$(pwd)
        echo -e "\nEnter the NAME of the directory containing the RAW data: "
        read RAW_DIR
        PATH_CHECK=$(validate_path "$RAW_DIR")
        
        if [ "$PATH_CHECK" == "VALID" ]; then
            RAW_DIR=$(echo "$RAW_DIR" | sed 's:/$::') # Remove trailing "/" from directory name if it exists
            echo -e "\nEnter the NAME of the directory containing the AUTOFLUORESCENCE data: "
            read AUTOF_DIR
            PATH_CHECK=$(validate_path "$AUTOF_DIR")
            
            if [ "$PATH_CHECK" == "VALID" ]; then
                AUTOF_DIR=$(echo "$AUTOF_DIR" | sed 's:/$::') # Remove trailing "/" from directory name if it exists
                break
            else
                echo -e "Directory:\n$AUTOF_DIR\ndoes not exist in:\n$DATA_PATH"
            fi    
        else
            echo -e "Directory:\n$RAW_DIR\ndoes not exist in:\n$DATA_PATH"
            echo "Please ensure you provided the correct experimental data directory"
        fi
    else
        echo -e "Please enter a valid path!"
    fi
done

while true; do
    echo -e "\nEnter the FILE NAME of the RAW data in the following format: "
    echo -e "\"raw_data_nameZ<Z,X>.tif\""
    echo -e "\t - Where Z<Z,X> tells us to anticipate X digits after the letter Z in the file name"
    echo -e "\t - Example: \"cfos_10_22_Z0000.ome.tif\" will become \"cfos_10_22_Z<Z,4>.ome.tif\""
    echo "Enter RAW data FILE NAME: "
    read RAW_FILE
    echo -e "\nDoes this look correct ([y]/n)? \"$RAW_FILE\""
    read INPUT
    confirm_file=$(return_bool "$INPUT")
    
    if [ "$confirm_file" == "True" ]; then
        RAW_FILE=$(echo "$RAW_FILE" | sed 's:^/::') # Remove leading "/" from file name if it exists
        break
    fi
done

RAW_PATH="$RAW_DIR/$RAW_FILE" # Set raw data path from experimental directory

while true; do
    echo -e "\nEnter the FILE NAME of the AUTOFLUORESCENCE data in the following format: "
    echo -e "\t - Example: \"autof_10_22_Z0000.ome.tif\" will become \"autof_10_22_Z<Z,4>.ome.tif\""
    echo -e "Enter AUTOFLUORESCENCE data FILE NAME: "
    read AUTOF_FILE
    echo -e "\nDoes this look correct ([y]/n)? \"$AUTOF_FILE\""
    read INPUT
    confirm_file=$(return_bool "$INPUT")
    
    if [ "$confirm_file" == "True" ]; then
        AUTOF_FILE=$(echo "$AUTOF_FILE" | sed 's:^/::') # Remove leading "/" from file name if it exists
        break
    fi
done

AUTOF_PATH="$AUTOF_DIR/$AUTOF_FILE" # Set autof data path from experimental directory

while true; do
    echo -e "\nEnter the x-resolution of the RAW data: "
    read RAW_X_RES
    echo -e "\nEnter the y-resolution of the RAW data: "
    read RAW_Y_RES
    echo -e "\nEnter the z-resolution of the RAW data: "
    read RAW_Z_RES
    echo -e "\nEnter the x-resolution of the AUTOFLUORESCENCE data: "
    read AUTOF_X_RES
    echo -e "\nEnter the y-resolution of the AUTOFLUORESCENCE data: "
    read AUTOF_Y_RES
    echo -e "\nEnter the z-resolution of the AUTOFLUORESCENCE data: "
    read AUTOF_Z_RES
    RAW_X_CHECK=$(validate_num "$RAW_X_RES")
    RAW_Y_CHECK=$(validate_num "$RAW_Y_RES")
    RAW_Z_CHECK=$(validate_num "$RAW_Z_RES")
    AUTOF_X_CHECK=$(validate_num "$AUTOF_X_RES")
    AUTOF_Y_CHECK=$(validate_num "$AUTOF_Y_RES")
    AUTOF_Z_CHECK=$(validate_num "$AUTOF_Z_RES")
    
    if [[ "$RAW_X_CHECK" == "VALID" && "$RAW_Y_CHECK" == "VALID" && "$RAW_Z_CHECK" == "VALID" && "$AUTOF_X_CHECK" == "VALID" && "$AUTOF_Y_CHECK" == "VALID" && "$AUTOF_Z_CHECK" == "VALID" ]]; then
        RAW_DATA_RES="($RAW_X_RES,$RAW_Y_RES,$RAW_Z_RES)"
        AUTOF_DATA_RES="($AUTOF_X_RES,$AUTOF_Y_RES,$AUTOF_Z_RES)"
        break
    else
        echo -e "\nPlease ensure all your entered resolutions are numbers!"
    fi
done

echo -e "\nDisplaying CellMap outputs to the terminal window can aid in troubleshooting."
while true; do
    echo "Do you want the program to display all outputs ([y]/n)? "
    read INPUT
    VERBOSITY=$(return_bool "$INPUT")
    if [ "$VERBOSITY" == "True" ] || [ "$VERBOSITY" == "False" ]; then
        break
    else
        echo "Invalid input. Please try again."
    fi
done

echo -e "\nRunning CellMap with checkpoints will allow you to examine your data after each step."
while true; do
    echo "Do you want to run the program with checkpoints ([y]/n)? "
    read INPUT
    CHECKPOINTS=$(return_bool "$INPUT")
    if [ "$CHECKPOINTS" == "True" ] || [ "$CHECKPOINTS" == "False" ]; then
        break
    else
        echo -e "Invalid input. Please try again.\n"
    fi
done


# Display collected information
echo -e "\nPlease verify the following information: "
echo -e "\t - Path to ClearMap: $CLEARMAP_PATH"
echo -e "\t - Path to Experimental Directory: $DATA_PATH"
echo -e "\t - Path from Experimental Directory to Raw Data: $RAW_PATH"
echo -e "\t - Path from Experimental Directory to Autofluorescence Data: $AUTOF_PATH"
echo -e "\t - Raw Data Resolution: $RAW_DATA_RES"
echo -e "\t - Autofluorescence Data Resolution: $AUTOF_DATA_RES"
echo -e "\t - Running in Silent Mode: $VERBOSITY"
echo -e "\t - Running with Checkpoints: $CHECKPOINTS"

while true; do
    echo -e "\nDoes this information look correct ([y]/n)? "
    read INPUT
    VERIFY_INFO=$(return_bool "$INPUT")
    if [ "$VERIFY_INFO" == "True" ]; then
        echo "SUCCESS!"
        break
    elif [ "$VERIFY_INFO" == "False" ]; then
        echo -e "\nExiting script...\n"
        exit 0
    else
        echo -e "Invalid input. Please try again.\n"
    fi
done

echo -e "\nExperimental Parameters Set!"

echo -e "\nAtlas Configuration"

echo -e "\nThe default atlas image was acquired in the sagittal plane:"
echo -e "\t - The x-axis spans from the ventral to the dorsal regions"
echo -e "\t - The y-axis spans from the rostral to the caudal regions"
echo -e "\t - The z-axis spans from the left to the right hemisphere"
echo "You can view this by unzipping and viewing the .tif file at: "
echo "ClearMap/Resources/Atlas/ABA_25um_reference.tif.zip"

echo -e "\nIt is critical to modify this orientation to match the orientation of your dataset"
echo "CellMap defines this default orientation as (1,2,3)"
echo "Using this definition, other orientations can be specified as follows: "
echo -e "\t - (-1,2,3) would invert the x-axis of the atlas"
echo -e "\t - (2,1,-3) would swap the x-axis and y-axis and invert the z-axis"
echo -e "\t - (3,1,2) would indicate a coronal image acquisition, where:"
echo -e "\t\t - The x-axis would move left to right across the hemispheres"
echo -e "\t\t - The y-axis would move from the ventral to the dorsal regions"
echo -e "\t\t - The z-axis would move from the rostral to the caudal regions"

while true; do
    echo -e "\nEnter the number (1, 2, or 3) in each position (X) for the desired atlas orientation:"
    
    echo "(X, _, _)"
    read ATLAS_X_ORIENTATION
    
    if [ ${#ATLAS_X_ORIENTATION} -eq 2 ]; then
        ABS_X="${ATLAS_X_ORIENTATION:1:1}"
    else
        ABS_X="$ATLAS_X_ORIENTATION"
    fi
    
    if [[ $ATLAS_X_ORIENTATION =~ ^(-?[123])$ ]]; then
        echo "($ATLAS_X_ORIENTATION, X, _)"
        read ATLAS_Y_ORIENTATION
        
        if [ ${#ATLAS_Y_ORIENTATION} -eq 2 ]; then
            ABS_Y="${ATLAS_Y_ORIENTATION:1:1}"
        else
            ABS_Y="$ATLAS_Y_ORIENTATION"
        fi
        
        if [[ $ATLAS_Y_ORIENTATION =~ ^(-?[123])$ ]] && [[ "$ABS_Y" != "$ABS_X" ]]; then
            echo "($ATLAS_X_ORIENTATION, $ATLAS_Y_ORIENTATION, X)"
            read ATLAS_Z_ORIENTATION
            
            if [ ${#ATLAS_Z_ORIENTATION} -eq 2 ]; then
                ABS_Z="${ATLAS_Z_ORIENTATION:1:1}"
            else
                ABS_Z="$ATLAS_Z_ORIENTATION"
            fi
            
            if [[ $ATLAS_Z_ORIENTATION =~ ^(-?[123])$ ]] && [[ "$ABS_Z" != "$ABS_X" ]] && [[ "$ABS_Z" != "$ABS_Y" ]]; then
                echo -e "\nWould you like to proceed with the following orientation ([y]/n)?"
                echo "($ATLAS_X_ORIENTATION, $ATLAS_Y_ORIENTATION, $ATLAS_Z_ORIENTATION)"
                read INPUT
                
                if [[ "$INPUT" =~ ^([yY][eE][sS]|[yY])$ ]]; then
                    echo -e "\nAtlas Orientation Set!"
                    break
                else
                    echo "Clearing orientation..."
                fi
            else
                echo "Please ensure your input only contains one number (-1/1, -2/2, -3/3) and has not already been chosen!"
            fi
        else 
            echo "Please ensure your input only contains one number (-1/1, -2/2, -3/3) and has not already been chosen!"
        fi
    else
        echo "Please ensure your input only contains one number (-1/1, -2/2, -3/3)!"
    fi
done

echo -e "\nFor accurate results, the atlas must be cropped to your experimental data."
echo -e "\t - The crop will be performed on the newly oriented atlas."
echo -e "\t\t - Note: Your newly oriented atlas can be replicated on ImageJ using the \"Reslice\" command"
echo -e "\t - Compare your experimental data to the newly oriented atlas to determine where the atlas should be cropped to best match the data"

while true; do
    echo -e "\nInput the desired crop for the minimum and maximum of each dimension."
    echo "For the atlas to remain uncropped for a given parameter, leave the input blank."
    
    echo -e "\nX-Axis Minimum: "
    read ATLAS_X_MIN
    if [[ -z "$ATLAS_X_MIN" ]]; then
        ATLAS_X_MIN="0"
    fi
    X_MIN_CHECK=$(validate_num "$ATLAS_X_MIN")
    
    echo -e "\nX-Axis Maximum:"
    read ATLAS_X_MAX
    if [[ -z "$ATLAS_X_MAX" ]]; then
        ATLAS_X_MAX="Maximum"
        X_MAX_CHECK=$(validate_num "1")
    else
        X_MAX_CHECK=$(validate_num "$ATLAS_X_MAX")
    fi
    
    echo -e "\nY-Axis Minimum: "
    read ATLAS_Y_MIN
    if [[ -z "$ATLAS_Y_MIN" ]]; then
        ATLAS_Y_MIN="0"
    fi
    Y_MIN_CHECK=$(validate_num "$ATLAS_Y_MIN")
    
    echo -e "\nY-Axis Maximum:"
    read ATLAS_Y_MAX    
    if [[ -z "$ATLAS_Y_MAX" ]]; then
        ATLAS_Y_MAX="Maximum"
        Y_MAX_CHECK=$(validate_num "1")
    else
        Y_MAX_CHECK=$(validate_num "$ATLAS_Y_MAX")
    fi
    
    echo -e "\nZ-Axis Minimum: "
    read ATLAS_Z_MIN
    if [[ -z "$ATLAS_Z_MIN" ]]; then
        ATLAS_Z_MIN="0"
    fi
    Z_MIN_CHECK=$(validate_num "$ATLAS_Z_MIN")

    echo -e "\nZ-Axis Maximum:"
    read ATLAS_Z_MAX
    if [[ -z "$ATLAS_Z_MAX" ]]; then
        ATLAS_Z_MAX="Maximum"
        Z_MAX_CHECK=$(validate_num "1")
    else
        Z_MAX_CHECK=$(validate_num "$ATLAS_Z_MAX")
    fi
    
    if [[ "$X_MIN_CHECK" == "VALID" && "$X_MAX_CHECK" == "VALID" && "$Y_MIN_CHECK" == "VALID" && "$Y_MAX_CHECK" == "VALID" && "$Z_MIN_CHECK" == "VALID" && "$Z_MAX_CHECK" == "VALID" ]]; then
        
        echo -e "\nCropped X-Axis: $ATLAS_X_MIN - $ATLAS_X_MAX"
        echo "Cropped Y-Axis: $ATLAS_Y_MIN - $ATLAS_Y_MAX"
        echo "Cropped Z-Axis: $ATLAS_Z_MIN - $ATLAS_Z_MAX"
        
        echo -e "\nWould you like to proceed with the following Atlas crop ([y]/n)?"
        read INPUT
        if [[ "$INPUT" =~ ^([yY][eE][sS]|[yY])$ ]]; then
            echo -e "\nAtlas Crop Set!"
            break
        else
            echo -e "\nClearing crop parameters..."
        fi
    else
        echo -e "\nPlease ensure all your entered crop parameters are valid numbers or blank!" # TODO: WHEN PASSING TO PYTHON SCRIPT, VERIFY THAT THE MIN IS ALWAYS SMALLER THAN THE MAX
    fi
done

echo -e "\nAtlas Configured!"

echo -e "\nCell Detection Parameter Configuration"

# PARAMETERS TO PASS
# $CLEARMAP_PATH
# $DATA_PATH
# $RAW_PATH
# $AUTOF_PATH
# $RAW_X_RES
# $RAW_Y_RES
# $RAW_Z_RES
# $AUTOF_X_RES
# $AUTOF_Y_RES
# $AUTOF_Z_RES
# $VERBOSITY
# $CHECKPOINTS
# $ATLAS_X_ORIENTATION
# $ATLAS_Y_ORIENTATION
# $ATLAS_Z_ORIENTATION
# $ATLAS_X_MIN
# $ATLAS_Y_MIN
# $ATLAS_Z_MIN
# $ATLAS_X_MAX
# $ATLAS_Y_MAX
# $ATLAS_Z_MAX

# ## CELL DETECTION PARAMETER CONFIGURATION
# # ILLUMINATION CORRECTION
# ILLUMINATION_FLATFIELD = "NULL"
# ILLUMINATION_BACKGROUND = "NULL"
# ILLUMINATION_SCALING = "NULL"
# ILLUMINATION_SAVE = "NULL"
# # BACKGROUND REMOVAL
# BACKGROUND_SHAPE = "NULL"
# BACKGROUND_FORM = "NULL"
# BACKGROUND_SAVE = "NULL"
# # EQUALIZATION
# EQ_PERCENTILE = "NULL"
# EQ_MAX = "NULL"
# EQ_SELEM = "NULL"
# EQ_SPACING = "NULL"
# EQ_INTERPOLATE = "NULL"
# EQ_SAVE = "NULL"
# # DoG FILTER
# DOG_SHAPE = "NULL"
# DOG_SIGMA = "NULL"
# DOG_SIGMA2 = "NULL"
# DOG_SAVE = "NULL"
# # MAXIMA DETECTION
# MAXIMA_HMAX = "NULL"
# MAXIMA_SHAPE = "NULL"
# MAXIMA_THRESHOLD = "NULL"
# MAXIMA_SAVE = "NULL"
# # SHAPE DETECTION
# SHAPE_THRESHOLD = "NULL"
# SHAPE_SAVE = "NULL"
# # INTENSITY DETECTION
# INTENSITY_METHOD = "NULL"
# INTENSITY_SHAPE = "NULL"
# INTENSITY_MEASURE = "NULL"
# INTENSITY_SAVE = "NULL"

# ## POST-PROCESSING CONFIGURATION
# # CELL FILTRATION
# FILTER_THRESHOLD = "NULL" # Potentially multiple
# # ANNOTATION
# ANNOTATE_NAME = "NULL" # Consider requiring by default
# ANNOTATE_ID = "NULL" 
# ANNOTATE_ACRONYM = "NULL"
# ANNOTATE_PARENT = "NULL"
# ANNOTATE_ATLAS = "NULL"
# ANNOTATE_ONTOLOGY = "NULL"
# ANNOTATE_COLOR = "NULL"
# ANNOTATE_STLVL = "NULL"
# ANNOTATE_HEMISPHERE = "NULL"
# # VOXELIZATION
# VOXEL_WEIGHT = "NULL"
# VOXEL_METHOD = "NULL"
# VOXEL_RADIUS = "NULL"
# VOXEL_KERNEL = "NULL"

