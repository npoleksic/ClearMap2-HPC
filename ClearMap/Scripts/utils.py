import sys  
import tty
import termios
import yaml
import csv
import json
import pandas as pd
from scipy.io import savemat
import shutil 
import os 
import tifffile as tiff
import datetime
import numpy as np
from PIL import Image

def checkpoint():
    
    """Pauses execution and waits for user key-press
    """
    
    print("\nPress any key to continue...")
    sys.stdin.read(1)
      
        
def read_config(path):
    
    """Reads yml configuration file into Python object
    
    Arguments
    ---------
        path : String
            Cell coordinates sorted by decreasing intensity.
    Returns
    -------
        data : array
            Configuration data
    """   
    
    try:
        with open(path, 'r') as config_file:
            data = yaml.safe_load(config_file)
        return data
    except FileNotFoundError:
        print("ERROR: CONFIGURATION FILE NOT FOUND")
        return None
    except yaml.YAMLError as exc:
        print("ERROR: YAML PARSING FAILED", exc)
        return None
        
        
def remove_overlap(source, filter_distance_min):
    
    """Removes overlapping cells after detection.
    
    Cells are removed if all three coordinates are within filter_distance_min of
    a cell of greater intensity, or if they are within half of filter_distance_min
    in the x and y direction, and 2x filter_distance_min in the z direction to correct
    for cells appearing in multiple slices due to out-of-plane excitation during imaging

    Arguments
    ---------
        source : array
            Cell coordinates sorted by decreasing intensity.
            
        filter_distance_min : int
            Minimum distance between cells.
    Returns
    -------
        source_filtered : array
            Input array with overlapping cells removed 
    """    
    
    indices_to_remove = set()
    source_coordinates = np.column_stack((source['x'], source['y'], source['z']))
    z_overlap_min = np.array([filter_distance_min/2, filter_distance_min/2, filter_distance_min*2])
    
    for i in range(len(source_coordinates)):
        if i not in indices_to_remove:
            current_point = source_coordinates[i]  
            
            diffs = abs(source_coordinates - current_point)
            
            close_indices = np.where(np.all(diffs < filter_distance_min, axis=1))[0]
            close_indices = close_indices[close_indices != i]
            
            close_z_indices = np.where(np.all(diffs < z_overlap_min, axis=1))[0]
            close_z_indices = close_z_indices[close_z_indices != i]

            if close_indices.size > 0:
                indices_to_remove.update(set(close_indices))
                indices_to_remove.update(set(close_z_indices))
        else:
            print("Removed overlapping cell at index: " + str(i))

    source_filtered = np.delete(source, list(indices_to_remove), axis=0)
    return source_filtered
    
    
    
def remove_universe(source):
    
    """Removes cells classified as "universe".
    
    Arguments
    ---------
        source : array
            Annotated cell detection results
    Returns
    -------
        source_filtered : array
            Input array with "universe" cells removed 
    """    
    
    universe_indices = np.where(source['name'] == 'universe')[0]
    source_filtered = np.delete(source, universe_indices, axis=0)
    
    return source_filtered
    
    
    
def transformation(coordinates):

    """Transforms detected cell coordinates onto atlas space
    
    Arguments
    ---------
        coordinates : array
            x, y, and z coordinates for each detected cell on experimental data
    Returns
    -------
        coordinates : array
            Corresponding x, y, and z coordinates transformed onto the brain atlas space
    """    
    
    import ClearMap.Alignment.Elastix as elx
    
    coordinates = elx.transform_points(
                    coordinates, sink=None, 
                    transform_directory=align_channel_outdir, 
                    binary=True, indices=False);

    coordinates = elx.transform_points(
                    coordinates, sink=None, 
                    transform_directory=align_reference_outdir,
                    binary=True, indices=False);

    return coordinates
    

    
def register_annotation(directory, annotation_file):
    
    """Aligns annotation atlas to fit the shape of the autofluorescence data
    
    Applies transformation parameters generated when aligning the reference atlas
    to the autofluorescence data and saves the registered annotation to the experimental
    directory.
    
    Arguments
    ---------
        directory : String
            Path to experimental data directory
            
        annotation_file : String
            Path to annotation atlas
    """   
    
    import ClearMap.Alignment.Elastix as elx

    auto_to_anno_path = os.path.join(directory, 'elastix_auto_to_anno')

    if not os.path.exists(auto_to_anno_path):
        os.makedirs(auto_to_anno_path)
        
    shutil.copy(os.path.join(directory, 'elastix_auto_to_reference/TransformParameters.0.txt'), auto_to_anno_path)
    shutil.copy(os.path.join(directory, 'elastix_auto_to_reference/TransformParameters.1.txt'), auto_to_anno_path)

    transform_anno_0 = os.path.join(auto_to_anno_path, 'TransformParameters.0.txt')
    transform_anno_1 = os.path.join(auto_to_anno_path, 'TransformParameters.1.txt')

    modify_transform_params(transform_anno_0)
    modify_transform_params(transform_anno_1)

    elx.transform(source=annotation_file, transform_parameter_file=transform_anno_1, result_directory=directory)
    os.rename(os.path.join(directory, 'result.tiff'), os.path.join(directory, 'auto_to_anno.tif'))

    
    
def modify_transform_params(transform_param_path):
    
    """Removes interpolation and changes output file type in transformation parameter file
    
    Arguments
    ---------
        transform_param_path : String
            Path to transformation parameter file
    """   
        
    with open(transform_param_path, 'r') as transform_file:
        lines = transform_file.readlines()

    for i, line in enumerate(lines):
        if "(FinalBSplineInterpolationOrder 3)" in line:
            lines[i] = line.replace("3", "0")
        if "(ResultImageFormat \"mhd\")" in line:
            lines[i] = line.replace("mhd", "tiff")
            break
    with open(transform_param_path, 'w') as transform_file:
        transform_file.writelines(lines)    
    
    
    
def get_region_stats(num_regions, directory, region_ids, region_parent_ids, res):

    """Computes experiment-specific region statistics
    
    Observed brain regions and their respective volumes are computed from the registered annotation
    atlas. The output csv file is read to obtain the number of detected cells per region, and the 
    density of cell expression is calculated by dividing the number of detected cells per region by
    the volume of the associated region.
    
    Arguments
    ---------
        num_regions : int
            Number of observable brain regions in atlas
            
        directory : String
            Path to experimental directory
            
        region_ids : array
            ID# for each brain region
            
        region_parent_ids : array
            Associated parent region ID# for each brain region
            
        res : array
            x, y, and z resolution of experimental data
            
    Returns
    -------
        region_counts : array
            Number of detected cells in each region
            
        region_volumes : array
            Volume in mm^3 of each region in experimental data
            
        region_densities : array
            Number of cells per mm^3 detected in each region
    """   
    
    import ClearMap.IO.IO as io

    region_volumes = np.zeros(num_regions, dtype=float)
    region_counts = np.zeros(num_regions)
    region_densities = np.zeros(num_regions)

    csv_in_path = os.path.join(directory, 'cells.csv')
    csv_in = pd.read_csv(csv_in_path)

    region_image_path = os.path.join(directory, 'auto_to_anno.tif')
    unique_regions, pixel_count = np.unique(io.as_source(region_image_path).array, return_counts=True)

    resolution = (res[0]*res[1]*res[2])/(10**9) # Converted from micrometers^3 to millimeters^3
    volumes = pixel_count*resolution

    # Obtain frequency counts for each region ID
    total_counts = csv_in[' id'].value_counts()

    # Allocate counts to appropriate regions and their parent regions
    for region_id, count in total_counts.items():
        current_id = region_id
        while current_id != 997 or current_id != 0:
            i, = np.where(region_ids == current_id)
            region_counts[i] += count
            current_id = region_parent_ids[i]

    # Allocate volumes to appropriate regions and their parent regions
    for i, volume in enumerate(volumes):
        current_id = unique_regions[i]
        while current_id != 997 or current_id != 0:
            j, = np.where(region_ids == current_id)
            region_volumes[j] += volume
            current_id = region_parent_ids[j]

    # Calculate cell expression densities
    region_densities = np.divide(region_counts, region_volumes, where=region_volumes!=0)
    region_densities[region_volumes == 0] = 0

    return region_counts, region_volumes, region_densities



def export_regions(num_regions, region_names, region_acronyms, region_ids, region_parent_ids, region_children, region_volumes, region_counts, region_densities, directory):

    """Exports region data into csv and MATLAB file types
    
    Arguments
    ---------
        num_regions : int
            Number of detected cells in each region
            
        region_names : array
            Name of each brain region
            
        region_acronyms : array
            Acronym for each brain region
            
        region_ids : array
            ID# for each brain region
            
        region_parent_ids : array
            Associated parent region ID# for each brain region
            
        region_children : array
            Associated child region names for each brain region
            
        region_volumes : array
            Volume in mm^3 of each region in experimental data
            
        region_counts : array
            Number of detected cells in each region
            
        region_densities : array
            Number of cells per mm^3 detected in each region
            
        directory : String
            Path to experimental data directory
    """   
    
    # Output region data as csv
    csv_out_data = np.column_stack((region_names, region_acronyms, region_ids, region_parent_ids, region_volumes, region_counts, region_densities))
    csv_headers = ["Name", "Acronym", "ID", "Parent ID", "Volume (mm^3)", "Count", "Count per mm^3"]
    csv_out_path = os.path.join(directory, 'regions.csv')
    with open(csv_out_path, 'w', newline='') as csv_out:
        writer = csv.writer(csv_out)
        writer.writerow(csv_headers)
        writer.writerows(csv_out_data)

    # Output MATLAB-compatible data
    region_data_arr = [];
    for i in range(num_regions):
        region_dict = {'Name': region_names[i],
                       'Acronym': region_acronyms[i],
                       'ID': region_ids[i],
                       'ParentID': region_parent_ids[i],
                       'Children': region_children[i],
                       'Volume': region_volumes[i],
                       'Count': region_counts[i],
                       'Density': region_densities[i]}
        region_data_arr.append(region_dict)

    mat_out_path = os.path.join(directory, 'region_data.mat')
    savemat(mat_out_path, {'region_data': region_data_arr})
    
    
    
def get_region_info(json_path):

    """Obtain basic information for each brain region from annotation file
    
    Arguments
    ---------
        json_path : String
            Path to refactored JSON annotation file
            
    Returns
    -------
        num_regions : int
            Number of detected cells in each region
            
        region_names : array
            Name of each brain region
            
        region_acronyms : array
            Acronym for each brain region
            
        region_ids : array
            ID# for each brain region
            
        region_parent_ids : array
            Associated parent region ID# for each brain region
            
        region_children : array
            Associated child region names for each brain region
    """   
    
    with open(json_path, 'r') as annotations:
        region_info = json.load(annotations)    

    num_regions = len(region_info) - 2
    region_names = np.zeros(num_regions, dtype=object)
    region_acronyms = np.zeros(num_regions, dtype=object)
    region_ids = np.zeros(num_regions)
    region_parent_ids = np.zeros(num_regions)
    region_children = np.zeros((num_regions), dtype=object)

    for i in range(num_regions):
        region = region_info[i+2]
        region_names[i] = region['name']
        region_acronyms[i] = region['acronym']
        region_ids[i] = region['id']
        region_parent_ids[i] = region['parent_structure_id']

    for i in range(num_regions): #findDirectChildren conversion
        region_children[i] = region_names[region_parent_ids == region_ids[i]]

    return num_regions, region_names, region_acronyms, region_ids, region_parent_ids, region_children
    
    

def upscale(directory, source_file, target_shape_file, output_file):

    """Upscales atlas images to match experimental data size
    
    Arguments
    ---------
        directory : String
            Path to experimental data directory
            
        source_file : String
            Path to image to be upscaled
            
        target_shape_file : String
            Path to image with the target shape
            
        output_file : String
            Filename for output image

    Returns
    -------
        target_rot : array
            Upscaled image data
    """
    
    # Initialization - set parameters
    source_mm = tiff.imread(source_file) 
    src_x, src_y, src_z = source_mm.shape[2], \ # define the source resolution out of the source annotation file
                          source_mm.shape[1], \
                          source_mm.shape[0]

    if len(target_shape_file) != 0: # define the resolution for the target file either manuel or match a target file so the annotation can be used as overlay  
        target_image        = tiff.imread(os.path.join(directory, target_shape_file))
        tar_x, tar_y, tar_z = target_image.shape[2], target_image.shape[1], target_image.shape[0]
        del target_image, target_shape_file
    else:
        tar_x, tar_y, tar_z = src_x*2, src_y*2, src_z*2 #matching resolution

    # 1. STEP: upscale x,y direction and hold z stable
    starttime = datetime.datetime.now()
    target_file = os.path.join(directory, "anno_upscaled_to_stitched.npy")
    target_mm = np.memmap(target_file, dtype="float32", mode="w+", shape=(src_z,tar_y,tar_x)) # create the final upscale file (just reserves the space on HDD)

    for i in range(source_mm.shape[0]):
        slice = np.array(Image.fromarray(source_mm[i]).resize((tar_x, tar_y), Image.NEAREST))
        target_mm[i] = slice
        target_mm.flush()
        if i!=0 and (round(i/source_mm.shape[0],2)*100)%10 == 0: 
            print(f"slice {i} of {len(source_mm[:,:,0])} ({round(i*100/source_mm.shape[0],1)}%)")

    print(f"S1 x,y upscale done: {len(source_mm[:,:,0])} slices upscaled in {datetime.datetime.now()-starttime}")

    # 2. STEP: upscale z direction and hold xy stable
    source_file = os.path.join(directory, "anno_upscaled_to_stitched.npy")
    source_mm = np.memmap(source_file, dtype="float32", mode="r", shape=(src_z,tar_y,tar_x)) # load the source registration file as mm (write protected) [z,y,x]
    
    target_file = os.path.join(directory, "anno_upscaled_to_rot-stitched.npy")
    target_rot = np.memmap(target_file, dtype="float32", mode="w+", shape=(tar_y,tar_z,tar_x)) # create the final upscale file (just reserves the space on HDD)

    source_mm = np.rot90(source_mm, 1, axes=(0,1))

    starttime2 = datetime.datetime.now()

    for i in range(source_mm.shape[0]):
        slice = np.array(Image.fromarray(source_mm[i]).resize((tar_x,tar_z), Image.NEAREST))
        target_rot[i] = slice
        target_rot.flush()

        if i!=0 and (round(i*100/source_mm.shape[0]))%20 == 0: 
            print(f"slice {i} of {len(source_mm[:,:,0])} ({round(i*100/source_mm.shape[0],1)}%)")

    target_rot = np.rot90(target_rot, -1, axes=(0,1))
    target_rot.flush()

    print(f"{len(source_mm[:,:,0])} slices upscaled in {datetime.datetime.now()-starttime2}")

    # 3. STEP: convert to tif
    with tiff.TiffWriter(os.path.join(directory, output_file), bigtiff=True) as tif:
        for i in range(target_rot.shape[0]):
            tif.save(target_rot[i], photometric='minisblack') # min-is-black
            if i!=0 and (round(i*100/source_mm.shape[0]))%20 == 0: 
                print(f"slice {i} of {target_rot.shape[0]} ({round(i*100/target_rot.shape[0],1)}%)")

    # 4. STEP: delete the working files
    os.remove(target_file)
    os.remove(source_file)

    print(f"Full processing time: {datetime.datetime.now()-starttime}")
    
    return target_rot