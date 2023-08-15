#!/bin/bash

echo -e "\n------------------------------------------------------------------------------------"
echo "--------------------------------------CELLMAP---------------------------------------"
echo "------------------------------------------------------------------------------------"

echo -e "\nThis script will setup the necessary environments for manually running CellMap."

echo -e "\nTo run a basic CellMap pipeline, exit this script and run ./run_cellmap.sh\n"

echo "The script will perform the following processes:"
echo -e "\t - Create and activate a CellMap-specific conda environment"
echo -e "\t - Install a python kernel that allows the user to manually run CellMap\n"

echo "Helpful links:"
echo -e "\t - ClearMap2 Source Code - github.com/ChristophKirst/ClearMap2/"
echo -e "\t - ClearMap2 Documentation - christophkirst.github.io/ClearMap2Documentation/"
echo -e "\t - ClearMap Tutorial [VIDEO] - https://youtu.be/-WehURPyIa8"

read -r -p "Would you like to proceed? ([y]/n): " response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]
then
    echo -e "\nInitializing..."
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
    echo -e "\nIn order to function properly, CellMap requires a specific environment."
    read -r -p "Would you like to install it? ([y]/n): " response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]
    then
        echo "Creating conda environment from ClearMapHPC.yml..."
        echo "(This may take a few minutes)"
        conda env create -f ClearMapHPC.yml -y
        echo "Environment successfully installed!"
        echo "Activating ClearMapHPC..."
        conda activate ClearMapHPC
        echo "ClearMapHPC successfully activated!"
    else
        echo -e "\nExiting script...\n"
        exit 0
    fi
fi

echo -e "\nChecking for kernel...\n"

jupyter kernelspec list | grep -q "clearmaphpc"
if [ $? -eq 0 ]; then
    echo "The python kernel \"ClearMapHPC\" already exists."
else
    echo "The python kernel \"ClearMapHPC\" is not installed."
    echo -e "\nTo run CellMap from a console editor, the \"ClearMapHPC\" kernel is required"
    read -r -p "Would you like to install it? ([y]/n): " response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]
    then
        echo "Installing ipykernel..."
        echo "(This may take a few minutes)"
        conda install -y ipykernel
        echo "ipykernel successfully installed!"
        echo "Creating kernel..."
        python -m ipykernel install --user --name ClearMapHPC --display-name “ClearMapHPC”
        echo "\"ClearMapHPC\" kernel successfully created!"
    else
        echo -e "\nExiting script...\n"
        exit 0
    fi
fi

echo -e "\nTo run CellMap from a console editor on JupyterHub:"
echo -e "\t - Open CellMap.py in the Scripts directory"
echo -e "\t - Right click inside the file and select \"Create Console for Editor\""
echo -e "\t - In the \"Select Kernel\" dropdown menu, select \"ClearMapHPC\""
echo -e "\t\t - This should open a console tab where you can view outputs"
echo -e "\t - Highlight desired code within CellMap.py"
echo -e "\t - Press [Shift]+[Enter]\n"