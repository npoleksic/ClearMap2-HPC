#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CellMapBash
=======

Adapted CellMap.py to be executed from a shell script

"""
__author__    = 'Christoph Kirst <christoph.kirst.ck@gmail.com>'
__license__   = 'GPLv3 - GNU General Pulic License v3 (see LICENSE)'
__copyright__ = 'Copyright © 2020 by Christoph Kirst'
__webpage__   = 'http://idisco.info'
__download__  = 'http://www.github.com/ChristophKirst/ClearMap2'

import sys  
import tty
import termios


def checkpoint():
    print("\nPress any key to continue...")
    sys.stdin.read(1)
    
if __name__ == "__main__":
    if len(sys.argv) < 23:
        print("SYSTEM ARG COUNT ERROR")
        sys.exit()
    
    clearmap_path = sys.argv[1]
    directory = sys.argv[2]
    expression_raw = sys.argv[3]
    expression_auto = sys.argv[4]
    
    raw_x_res = float(sys.argv[5])
    raw_y_res = float(sys.argv[6])
    raw_z_res = float(sys.argv[7])
    autof_x_res = float(sys.argv[8])
    autof_y_res = float(sys.argv[9])
    autof_z_res = float(sys.argv[10])
    if(sys.argv[11] == "True"):
        checkpoints = True
    else:
        checkpoints = False
    
    #Convert to integers
    x_orient = int(sys.argv[12])
    y_orient = int(sys.argv[13])
    z_orient = int(sys.argv[14])
    
    if(sys.argv[15] == "0"):
        x_min = None
    else:
        x_min = int(sys.argv[15])
    if(sys.argv[16] == "0"):
        y_min = None
    else:
        y_min = int(sys.argv[16])
    if(sys.argv[17] == "0"):
        z_min = None
    else:
        z_min = int(sys.argv[17])
        
    if(sys.argv[18] == "Maximum"):
        x_max = None
    else:
        x_max = int(sys.argv[18])
    if(sys.argv[19] == "Maximum"):
        y_max = None
    else:
        y_max = int(sys.argv[19])
    if(sys.argv[20] == "Maximum"):
        z_max = None
    else:
        z_max = int(sys.argv[20])
        
    filter_min = int(sys.argv[21])
    filter_max = int(sys.argv[22])
    
    sys.path.append(clearmap_path)
    from ClearMap.Environment import *

    ws = wsp.Workspace('CellMap', directory=directory);
    ws.update(raw=expression_raw, autofluorescence=expression_auto)
    ws.info()

    ws.debug = False

    resources_directory = settings.resources_path

    annotation_file, reference_file, distance_file=ano.prepare_annotation_files(
        slicing=(slice(x_min,x_max),slice(y_min,y_max),slice(z_min,z_max)), orientation=(x_orient,y_orient,z_orient),
        overwrite=False, verbose=True);

    align_channels_affine_file   = io.join(resources_directory, 'Alignment/align_affine.txt')
    align_reference_affine_file  = io.join(resources_directory, 'Alignment/align_affine.txt')
    align_reference_bspline_file = io.join(resources_directory, 'Alignment/align_bspline.txt')
    
    if checkpoints:
        print("\nATLAS CHECKPOINT")
        print("\nNavigate to ClearMap/Resources/Atlas and ensure the newly generated reference atlas matches the orientation and crop of your experimental data.")
        checkpoint()
    
    print("\nResampling and aligning channels...\n")

    source = ws.source('raw');
    sink   = ws.filename('stitched')
    io.delete_file(sink)
    io.convert(source, sink, processes=16, verbose=True);

    resample_parameter = {
        "source_resolution" : (raw_x_res,raw_y_res,raw_z_res),
        "sink_resolution"   : (25,25,25),
        "processes" : 16,
        "verbose" : True,             
        };

    io.delete_file(ws.filename('resampled'))

    res.resample(ws.filename('stitched'), sink=ws.filename('resampled'), **resample_parameter)

    resample_parameter_auto = {
        "source_resolution" : (autof_x_res,autof_y_res,autof_z_res),
        "sink_resolution"   : (25,25,25),
        "processes" : 16,
        "verbose" : True,                
        };    

    res.resample(ws.filename('autofluorescence'), sink=ws.filename('resampled', postfix='autofluorescence'), **resample_parameter_auto)

    align_channels_parameter = {            
        "processes" : 16,
        "moving_image" : ws.filename('resampled', postfix='autofluorescence'),
        "fixed_image"  : ws.filename('resampled'),
        "affine_parameter_file"  : align_channels_affine_file,
        "bspline_parameter_file" : None,
        "result_directory" :  ws.filename('resampled_to_auto')
        }; 

    elx.align(**align_channels_parameter);

    align_reference_parameter = {            
        "processes" : 16,
        "moving_image" : reference_file,
        "fixed_image"  : ws.filename('resampled', postfix='autofluorescence'),
        "affine_parameter_file"  :  align_reference_affine_file,
        "bspline_parameter_file" :  align_reference_bspline_file,
        "result_directory" :  ws.filename('auto_to_reference')
        };

    elx.align(**align_reference_parameter);

    if checkpoints:
        print("\nALIGNMENT CHECKPOINT")
        print("\nFrom the newly generated files in your experimental directory, compare: ")
        print("\t - resampled.tif to elastix_resampled_to_auto/result.0.mhd")
        print("\t - resampled_autofluorescence.tif to elastix_auto_to_reference/result.1.mhd")
        print("Ensure the files are properly aligned in shape and slicing")
        checkpoint()

    print("\nDetecting cells...\n")

    cell_detection_parameter = cells.default_cell_detection_parameter.copy();
    
    cell_detection_parameter['illumination_correction']['flatfield'] = None
    cell_detection_parameter['illumination_correction']['background'] = None
    cell_detection_parameter['illumination_correction']['scaling'] = 'mean'
    cell_detection_parameter['illumination_correction']['save'] = None
    
    cell_detection_parameter['background_correction']['shape'] = (7,7) #(9,9)
    cell_detection_parameter['background_correction']['form'] = 'Disk'
    cell_detection_parameter['background_correction']['save'] = None
    
    cell_detection_parameter['equalization'] = None
    # cell_detection_parameter['equalization']['percentile'] = None
    # cell_detection_parameter['equalization']['max_value'] = None
    # cell_detection_parameter['equalization']['selem'] = None
    # cell_detection_parameter['equalization']['spacing'] = None
    # cell_detection_parameter['equalization']['interpolate'] = None
    # cell_detection_parameter['equalization']['save'] = None

    cell_detection_parameter['dog_filter']['shape'] = None
    cell_detection_parameter['dog_filter']['sigma'] = None
    cell_detection_parameter['dog_filter']['sigma2'] = None
    cell_detection_parameter['dog_filter']['save'] = None
    
    cell_detection_parameter['maxima_detection']['h_max'] = None
    cell_detection_parameter['maxima_detection']['shape'] = 5
    cell_detection_parameter['maxima_detection']['threshold'] = 3500 #0
    cell_detection_parameter['maxima_detection']['valid'] = True
    cell_detection_parameter['maxima_detection']['save'] = None

    cell_detection_parameter['shape_detection']['threshold'] = 2000 #700
    cell_detection_parameter['shape_detection']['save'] = None
    
    cell_detection_parameter['intensity_detection']['method'] = 'max'
    cell_detection_parameter['intensity_detection']['shape'] = 3
    cell_detection_parameter['intensity_detection']['measure'] = ['source']; 
    # cell_detection_parameter['intensity_detection']['save'] = None

    processing_parameter = cells.default_cell_detection_processing_parameter.copy();
    processing_parameter.update(
        processes = 12,
        size_max = 45,
        size_min = 20,
        overlap  = 10,
        verbose = True
        )

    cells.detect_cells(ws.filename('stitched'), ws.filename('cells', postfix='raw'),
                       cell_detection_parameter=cell_detection_parameter, 
                       processing_parameter=processing_parameter)  
    
    if checkpoints:
        print("\nCell detection complete!")
        checkpoint()
        
    print("\nFiltering and annotating cells...\n")

    source = ws.source('cells', postfix='raw')

    thresholds = {
        'source' : None,
        'size'   : (filter_min,filter_max)
        }

    cells.filter_cells(source = ws.filename('cells', postfix='raw'), 
                       sink = ws.filename('cells', postfix='filtered'), 
                       thresholds=thresholds); 

    source = ws.source('cells', postfix='filtered')

    def transformation(coordinates):
        coordinates = res.resample_points(
                        coordinates, sink=None, orientation=None, 
                        source_shape=io.shape(ws.filename('stitched')), 
                        sink_shape=io.shape(ws.filename('resampled')));

        coordinates = elx.transform_points(
                        coordinates, sink=None, 
                        transform_directory=ws.filename('resampled_to_auto'), 
                        binary=True, indices=False);

        coordinates = elx.transform_points(
                        coordinates, sink=None, 
                        transform_directory=ws.filename('auto_to_reference'),
                        binary=True, indices=False);

        return coordinates;

    coordinates = np.array([source[c] for c in 'xyz']).T;

    coordinates_transformed = transformation(coordinates);

    ano.set_annotation_file(annotation_file)   # CONFIGURE ANNOTATION
    label = ano.label_points(coordinates_transformed, key='order');
    names = ano.convert_label(label, key='order', value='name');
    ID = ano.convert_label(label, key='order', value='id');
    # acronym = ano.convert_label(label, key='order', value='acronym');  
    parent_ID = ano.convert_label(label, key='order', value='parent_structure_id');

    coordinates_transformed.dtype=[(t,float) for t in ('xt','yt','zt')]
    label = np.array(label, dtype=[('order', int)]);
    names = np.array(names, dtype=[('name', 'U256')]);
    ID = np.array(ID, dtype=[('id', int)]);
    # acronym = np.array(acronym, dtype=[('acronym', 'U256')])
    parent_ID = np.array(parent_ID, dtype=[('parent_structure_id', int)]);

    import numpy.lib.recfunctions as rfn

    cells_data = rfn.merge_arrays([source[:], coordinates_transformed, label, ID, parent_ID, names], flatten=True, usemask=False)

    io.write(ws.filename('cells'), cells_data)
    
    if checkpoints:
        print("\nCell annotation complete!")
        checkpoint()

    print("\nExporting data and beginning cell voxelization...\n")
    source = ws.source('cells');
    header = ', '.join([h for h in source.dtype.names]);
    np.savetxt(ws.filename('cells', extension='csv'), source[:], header=header, delimiter=',', fmt='%s')

    source = ws.source('cells');

    clearmap1_format = {'points' : ['x', 'y', 'z'], 
                        'points_transformed' : ['xt', 'yt', 'zt'],
                        'intensities' : ['source', 'dog', 'background', 'size']}

    for filename, names in clearmap1_format.items():
        sink = ws.filename('cells', postfix=['ClearMap1', filename]);
        data = np.array([source[name] if name in source.dtype.names else np.full(source.shape[0], np.nan) for name in names]);
        io.write(sink, data);

    source = ws.source('cells')

    coordinates = np.array([source[n] for n in ['xt','yt','zt']]).T;
    intensities = source['source'];
    
    voxelization_parameter = dict( # CONFIGURE VOXELIZATION PARAMETERS
          shape = io.shape(annotation_file), 
          dtype = None, 
          weights = None,
          method = 'sphere', 
          radius = (7,7,7), 
          kernel = None, 
          processes = 16, 
          verbose = True
          )

    vox.voxelize(coordinates, sink=ws.filename('density', postfix='counts'), **voxelization_parameter);  

    voxelization_parameter = dict( # CONFIGURE VOXELIZATION PARAMETERS
          shape = io.shape(annotation_file),
          dtype = None, 
          weights = intensities,
          method = 'sphere', 
          radius = (7,7,7), 
          kernel = None, 
          processes = 16, 
          verbose = True
          )

    vox.voxelize(coordinates, sink=ws.filename('density', postfix='intensities'), **voxelization_parameter);
    print("CellMap Pipeline Complete!")
