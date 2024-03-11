#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CellMap
=======

Adapted CellMap.py to be executed from a shell script with YAML configuration file

"""
__author__    = 'Christoph Kirst <christoph.kirst.ck@gmail.com>'
__license__   = 'GPLv3 - GNU General Pulic License v3 (see LICENSE)'
__copyright__ = 'Copyright © 2020 by Christoph Kirst'
__webpage__   = 'http://idisco.info'
__download__  = 'http://www.github.com/ChristophKirst/ClearMap2'

from utils import *

if __name__ == "__main__":
    if len(sys.argv) < 1:
        print("ERROR: SYSTEM ARG COUNT")
        sys.exit()
    clearmap_path = sys.argv[1]
    sys.path.append(clearmap_path)
    config = read_config('config_parameters.yml')
    
    if config:
        directory = config.get('experiment_path')
        expression_raw = config.get('raw_data_path')
        expression_auto = config.get('autof_data_path')

        raw_x_res = config.get('raw_x_resolution')
        raw_y_res = config.get('raw_y_resolution')
        raw_z_res = config.get('raw_z_resolution')
        autof_x_res = config.get('autof_x_resolution')
        autof_y_res = config.get('autof_y_resolution')
        autof_z_res = config.get('autof_z_resolution')
        checkpoints = config.get('include_checkpoints')

        #Convert to integers
        x_orient = config.get('x_orientation')
        y_orient = config.get('y_orientation')
        z_orient = config.get('z_orientation')
        
        x_min = config.get('atlas_x_min')
        x_max = config.get('atlas_x_max')
        y_min = config.get('atlas_y_min')
        y_max = config.get('atlas_y_max')
        z_min = config.get('atlas_z_min')
        z_max = config.get('atlas_z_max')

        if(x_min == 0):
            x_min = None
        if(x_max == "MAX"):
            x_max = None
        if(y_min == 0):
            y_min = None
        if(y_max == "MAX"):
            y_max = None
        if(z_min == 0):
            z_min = None
        if(z_max == "MAX"):
            z_max = None
            
        illumination = config.get('illumination_correction')
        illumination_flatfield = config.get('illumination_correction_flatfield')
        illumination_background = config.get('illumination_correction_background')
        illumination_scaling = config.get('illumination_correction_scaling')
        illumination_save = config.get('illumination_correction_save')
        
        if not illumination_flatfield:
            illumination_flatfield = None
        else:
            illumination_flatfield = directory + "/" + illumination_flatfield
        if not illumination_background:
            illumination_background = None
        else:
            illumination_background = directory + "/" + illumination_background
        if not illumination_scaling:
            illumination_scaling = None
        if illumination_save:
            illumination_save = ws.filename('cells', postfix='illumination')
        else:
            illumination_save = None
            
        background = config.get('background_correction')
        b_shape = config.get('background_correction_shape')
        b_form = config.get('background_correction_form')
        b_save = config.get('background_correction_save')
        
        if not b_shape:
            b_shape = None
        else:
            b_shape = tuple(b_shape)
        if not b_form:
            b_form = None
        if b_save:
            b_save = ws.filename('cells', postfix='background')
        else:
            b_save = None
            
        equalization = config.get('equalization')
        e_percentile = config.get('equalization_percentile')
        e_max_value = config.get('equalization_max_value')
        e_selem = config.get('equalization_selem')
        e_spacing = config.get('equalization_spacing')
        e_interpolate = config.get('equalization_interpolate')
        e_save = config.get('equalization_save')
        
        if not e_percentile:
            e_percentile = None
        else:
            e_percentile = tuple(e_percentile)
        if not e_max_value:
            e_max_value = None
        if not e_selem:
            e_selem = None
        else:
            e_selem = tuple(e_selem)
        if not e_spacing:
            e_spacing = None
        else:
            e_spacing = tuple(e_spacing)
        if not e_interpolate:
            e_interpolate = None
        if e_save:
            e_save = ws.filename('cells', postfix='equalization')
        else:
            e_save = None
            
        dog = config.get('dog_filter')
        d_shape = config.get('dog_filter_shape')
        d_sigma = config.get('dog_filter_sigma')
        d_sigma2 = config.get('dog_filter_sigma2')
        d_save = config.get('dog_filter_save')
        
        if not d_shape:
            d_shape = None
        else:
            d_shape = tuple(d_shape)
        if not d_sigma:
            d_sigma = None
        else:
            d_sigma = tuple(d_sigma)
        if not d_sigma2:
            d_sigma2 = None
        else:
            d_sigma2 = tuple(d_sigma2)
        if d_save:
            d_save = ws.filename('cells', postfix='dog')
        else:
            d_save = None
            
        maxima = config.get('maxima_detection')
        m_h_max = config.get('maxima_detection_h_max')
        m_shape = config.get('maxima_detection_shape')
        m_thresh = config.get('maxima_detection_threshold')
        m_valid = config.get('maxima_detection_valid')
        m_save = config.get('maxima_detection_save')
        
        if not m_h_max:
            m_h_max = None
        if not m_shape:
            m_shape = None
        # else:
        #     m_shape = tuple(m_shape)
        if not m_thresh:
            m_thresh = None
        if m_save:
            m_save = ws.filename('cells', postfix='maxima')
        else:
            m_save = None

        shape_detection = config.get('shape_detection')
        s_thresh = config.get('shape_detection_threshold')
        s_save = config.get('shape_detection_save')

        if not s_thresh:
            s_thresh = None
        if s_save:
            s_save = ws.filename('cells', postfix='shape')
        else:
            s_save = None
            
        intensity = config.get('intensity_detection')
        intensity_method = config.get('intensity_detection_method')
        intensity_shape = config.get('intensity_detection_shape')
        intensity_measure = config.get('intensity_detection_measure')
        
        if not intensity_method:
            intensity_method = None
        if not intensity_shape:
            intensity_shape = None
        if not intensity_measure:
            intensity_measure = None
        else:
            intensity_measure = ['source'];
        
        filter_size_min = config.get('filter_size_min')
        filter_size_max = config.get('filter_size_max')
        filter_intensity_min = config.get('filter_intensity_min')
        filter_intensity_max = config.get('filter_intensity_max')
        filter_distance_min = config.get('filter_distance_min')
        
        if(filter_size_max == "MAX"):
            filter_size_max = None
        if(filter_intensity_max == "MAX"):
            filter_intensity_max = None
            
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

    if illumination:
        cell_detection_parameter['illumination_correction']['flatfield'] = illumination_flatfield
        cell_detection_parameter['illumination_correction']['background'] = illumination_background
        cell_detection_parameter['illumination_correction']['scaling'] = illumination_scaling
        cell_detection_parameter['illumination_correction']['save'] = illumination_save
    else:
        cell_detection_parameter['illumination_correction'] = None
        
    if background:
        cell_detection_parameter['background_correction']['shape'] = b_shape
        cell_detection_parameter['background_correction']['form'] = b_form
        cell_detection_parameter['background_correction']['save'] = b_save
    else:
        cell_detection_parameter['background_correction'] = None
    
    if equalization:
        cell_detection_parameter['equalization']['percentile'] = e_percentile
        cell_detection_parameter['equalization']['max_value'] = e_max_value
        cell_detection_parameter['equalization']['selem'] = e_selem
        cell_detection_parameter['equalization']['spacing'] = e_spacing
        cell_detection_parameter['equalization']['interpolate'] = e_interpolate
        cell_detection_parameter['equalization']['save'] = e_save
    else:
        cell_detection_parameter['equalization'] = None

    if dog:
        cell_detection_parameter['dog_filter']['shape'] = d_shape
        cell_detection_parameter['dog_filter']['sigma'] = d_sigma
        cell_detection_parameter['dog_filter']['sigma2'] = d_sigma2
        cell_detection_parameter['dog_filter']['save'] = d_save
    else:
        cell_detection_parameter['dog_filter'] = None
    
    if maxima:
        cell_detection_parameter['maxima_detection']['h_max'] = m_h_max
        cell_detection_parameter['maxima_detection']['shape'] = m_shape
        cell_detection_parameter['maxima_detection']['threshold'] = m_thresh
        cell_detection_parameter['maxima_detection']['valid'] = m_valid
        cell_detection_parameter['maxima_detection']['save'] = m_save
    else:
        cell_detection_parameter['maxima_detection'] = None
        
    if shape_detection:
        cell_detection_parameter['shape_detection']['threshold'] = s_thresh
        cell_detection_parameter['shape_detection']['save'] = s_save
    else:
        cell_detection_parameter['shape_detection'] = None
    
    if intensity:
        cell_detection_parameter['intensity_detection']['method'] = intensity_method
        cell_detection_parameter['intensity_detection']['shape'] = intensity_shape
        cell_detection_parameter['intensity_detection']['measure'] = intensity_measure
    else:
        cell_detection_parameter['intensity_detection'] = None
        
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
        'source' : (filter_intensity_min, filter_intensity_max),
        'size': (filter_size_min, filter_size_max)
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
    names = np.array(names, dtype=[('name', 'U256')])
    ID = np.array(ID, dtype=[('id', int)]);
    # acronym = np.array(acronym, dtype=[('acronym', 'U256')])
    parent_ID = np.array(parent_ID, dtype=[('parent_structure_id', 'U256')]);

    import numpy.lib.recfunctions as rfn

    cells_data = rfn.merge_arrays([source[:], coordinates_transformed, label, ID, parent_ID, names], flatten=True, usemask=False)

    io.write(ws.filename('cells'), cells_data)
    
    if checkpoints:
        print("\nCell annotation complete!")
        checkpoint()
        
    print("\nExporting data and beginning cell voxelization...\n")
    source = ws.source('cells');
    header = ', '.join([h for h in source.dtype.names]);
    source = remove_universe(source.array)
    source = np.flip(np.sort(source, order=['source']),axis=0)
    source = remove_overlap(source, filter_distance_min) #TODO: Modify remove_overlap to sort source by decreasing intensity so that eliminating nearby detected "cells" is easier
    source = np.sort(source, order=['z'])
    np.savetxt(ws.filename('cells', extension='csv'), source, header=header, delimiter=',', fmt='%s')

    source = ws.source('cells');

    coordinates = np.array([source[n] for n in ['xt','yt','zt']]).T;
    intensities = source['source'];
    
    voxelization_parameter = dict( # CONFIGURE VOXELIZATION PARAMETERS
          shape = io.shape(annotation_file), 
          dtype = None, 
          weights = None,
          method = 'sphere', 
          radius = (1,1,1), 
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
          radius = (1,1,1), 
          kernel = None, 
          processes = 16, 
          verbose = True
          )

    vox.voxelize(coordinates, sink=ws.filename('density', postfix='intensities'), **voxelization_parameter);
        
    print("\nProcessing cell count results and registering annotation files...\n")
    
    # Read modified annotation file into json object
    
    json_path = clearmap_path + '/ClearMap/Resources/Atlas/annotations_reform.json'
    
    num_regions, region_names, region_acronyms, region_ids, region_parent_ids, region_children = get_region_info(json_path)

    register_annotation(directory)
    
    region_counts, region_volumes, region_densities = get_region_stats(num_regions, directory, region_ids, region_parent_ids)
    
    print("\nExporting cell count statistics...\n")
    
    export_regions(num_regions, region_names, region_acronyms, region_ids, region_parent_ids, region_children, region_volumes, region_counts, region_densities, directory)
    
    print("CellMap Pipeline Complete!")