#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CellMap
=======

Adapted original ClearMap2.0 CellMap.py script to be executed from a shell script with YAML configuration file

"""
__license__   = 'GPLv3 - GNU General Pulic License v3 (see LICENSE)'
__copyright__ = 'Copyright © 2020 by Christoph Kirst'

# from utils import *
# clearmap_path = '/home/npoleksic/ClearMap2-HPC'
# sys.path.append(clearmap_path)
# from ClearMap.Environment import *
# yml_file = 'config_parameters_ga2.yml'
# config = read_config(os.path.join(clearmap_path, yml_file))

from utils import *

if __name__ == "__main__":
    
    # Verify that script is run correctly from terminal
    if len(sys.argv) < 1:
        print("ERROR: SYSTEM ARG COUNT")
        sys.exit()
    clearmap_path = sys.argv[1]
    
    sys.path.append(clearmap_path)
    
    # Import supplementary ClearMap modules
    from ClearMap.Environment import *
    yml_file = 'config_parameters.yml'
    
    # Read parameters from YML file
    config = read_config(yml_file)

    if config:
        directory = config.get('experiment_path')
        shutil.copy(yml_file, directory)

        ws = wsp.Workspace('CellMap', directory=directory)

        expression_raw = config.get('raw_data_path')
        expression_auto = config.get('autof_data_path')

        if len(io.shape(os.path.join(directory, expression_raw))) == 2:
            janky_tiff = True
        else:
            janky_tiff = False

        # Initialize experimental environment
        cfos_file = os.path.join(directory, 'cfos.npy')
        autof_file = os.path.join(directory, 'autof.npy')
    
        if not os.path.exists(cfos_file):
            print("\nConverting raw data channel to npy array...\n")
            if janky_tiff:
                cfos_data = np.transpose(tiff.imread(os.path.join(directory, expression_raw)), (2,1,0))
                io.convert(cfos_data, cfos_file, processes=32, verbose=True)
            else:
                io.convert(os.path.join(directory, expression_raw), cfos_file, processes=32, verbose=True)
    
        if not os.path.exists(autof_file):
            print("\nConverting autofluorescence data channel to npy array...\n")
            if janky_tiff:
                autof_data = np.transpose(tiff.imread(os.path.join(directory, expression_auto)), (2,1,0))
                io.convert(autof_data, autof_file, processes=32, verbose=True)
            else:
                io.convert(os.path.join(directory, expression_auto), autof_file, processes=32, verbose=True)

        target_raw_shape = io.shape(cfos_file)
        target_auto_shape = io.shape(autof_file)

        save_crop = config.get('save_crop')
        save_preproc = config.get('save_preprocessing')
        skip_registration = config.get('skip_registration')
        skip_detection = config.get('skip_detection')
        auto_thresh = config.get('auto_thresh')
        
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
        
        raw_x_min = config.get('raw_x_min')
        raw_x_max = config.get('raw_x_max')
        raw_y_min = config.get('raw_y_min')
        raw_y_max = config.get('raw_y_max')
        raw_z_min = config.get('raw_z_min')
        raw_z_max = config.get('raw_z_max')

        if config.get('raw_x_max') == "MAX":
            target_raw_shape = (target_raw_shape[0] - raw_x_min, target_raw_shape[1], target_raw_shape[2])
            raw_x_max = None
        else:
            target_raw_shape = (raw_x_max - raw_x_min, target_raw_shape[1], target_raw_shape[2])

        if config.get('raw_y_max') == "MAX":
            target_raw_shape = (target_raw_shape[0], target_raw_shape[1] - raw_y_min, target_raw_shape[2])
            raw_y_max = None
        else:
            target_raw_shape = (target_raw_shape[0], raw_y_max - raw_y_min, target_raw_shape[2])

        if config.get('raw_z_max') == "MAX":
            target_raw_shape = (target_raw_shape[0], target_raw_shape[1], target_raw_shape[2] - raw_z_min)
            raw_z_max = None
        else:
            target_raw_shape = (target_raw_shape[0], target_raw_shape[1], raw_z_max - raw_z_min)
        
        if(raw_x_min == 0):
            raw_x_min = None
        if(raw_y_min == 0):
            raw_y_min = None
        if(raw_z_min == 0):
            raw_z_min = None

        crop_match = config.get('crop_match')

        if crop_match:
            auto_x_min = raw_x_min
            auto_x_max = raw_x_max
            auto_y_min = raw_y_min
            auto_y_max = raw_y_max
            auto_z_min = raw_z_min
            auto_z_max = raw_z_max
            target_auto_shape = target_raw_shape
        else: 
            auto_x_min = config.get('auto_x_min')
            auto_x_max = config.get('auto_x_max')
            auto_y_min = config.get('auto_y_min')
            auto_y_max = config.get('auto_y_max')
            auto_z_min = config.get('auto_z_min')
            auto_z_max = config.get('auto_z_max')
    
            if config.get('auto_x_max') == "MAX":
                target_auto_shape = (target_auto_shape[0] - auto_x_min, target_auto_shape[1], target_auto_shape[2])
                auto_x_max = None
            else:
                target_auto_shape = (auto_x_max - auto_x_min, target_auto_shape[1], target_auto_shape[2])
    
            if config.get('auto_y_max') == "MAX":
                target_auto_shape = (target_auto_shape[0], target_auto_shape[1] - auto_y_min, target_auto_shape[2])
                auto_y_max = None
            else:
                target_auto_shape = (target_auto_shape[0], auto_y_max - auto_y_min, target_auto_shape[2])
    
            if config.get('auto_z_max') == "MAX":
                target_auto_shape = (target_auto_shape[0], target_auto_shape[1], target_auto_shape[2] - auto_z_min)
                auto_z_max = None
            else:
                target_auto_shape = (target_auto_shape[0], target_auto_shape[1], auto_z_max - auto_z_min)
            
            if(auto_x_min == 0):
                auto_x_min = None
            if(auto_y_min == 0):
                auto_y_min = None
            if(auto_z_min == 0):
                auto_z_min = None
        
        atlas_x_min = config.get('atlas_x_min')
        atlas_x_max = config.get('atlas_x_max')
        atlas_y_min = config.get('atlas_y_min')
        atlas_y_max = config.get('atlas_y_max')
        atlas_z_min = config.get('atlas_z_min')
        atlas_z_max = config.get('atlas_z_max')

        if(atlas_x_min == 0):
            atlas_x_min = None
        if(atlas_x_max == "MAX"):
            atlas_x_max = None
        if(atlas_y_min == 0):
            atlas_y_min = None
        if(atlas_y_max == "MAX"):
            atlas_y_max = None
        if(atlas_z_min == 0):
            atlas_z_min = None
        if(atlas_z_max == "MAX"):
            atlas_z_max = None
            
        m_shape = config.get('maxima_detection_shape')
        m_thresh = config.get('maxima_detection_threshold')
        m_save = config.get('maxima_detection_save')
        
        if not m_shape:
            m_shape = None
        if not m_thresh:
            m_thresh = None
        if m_save:
            m_save = ws.filename('cells', postfix='maxima')
        else:
            m_save = None

        s_thresh = config.get('shape_detection_threshold')
        s_save = config.get('shape_detection_save')

        if not s_thresh:
            s_thresh = None
        if s_save:
            s_save = ws.filename('cells', postfix='shape')
        else:
            s_save = None
            
        intensity_method = config.get('intensity_detection_method')
        intensity_shape = config.get('intensity_detection_shape')
        
        if not intensity_method:
            intensity_method = None
        if not intensity_shape:
            intensity_shape = None
        
        filter_size_min = config.get('filter_size_min')
        filter_size_max = config.get('filter_size_max')
        filter_intensity_min = config.get('filter_intensity_min')
        filter_intensity_max = config.get('filter_intensity_max')
        filter_distance_min = config.get('filter_distance_min')
        
        if(filter_size_max == "MAX"):
            filter_size_max = None
        if(filter_intensity_max == "MAX"):
            filter_intensity_max = None
            
    ws.update(raw='cfos.npy', autofluorescence='autof.npy', stitched='cfos.npy')
    ws.debug = False


    # CROPPING USER DATA
    if not io.shape(cfos_file) == target_raw_shape:
        print("\nCropping raw data channel to specified dimensions...\n")
        if not janky_tiff:
            cfos_data = np.load(cfos_file)
        cfos_data = cfos_data[raw_x_min:raw_x_max, raw_y_min:raw_y_max, raw_z_min:raw_z_max]
        io.convert(cfos_data, cfos_file, processes=32, verbose=True)
        if save_crop:
            io.convert(cfos_data, os.path.join(directory, 'cfos.tif'), processes=32, verbose=True)
        del cfos_data

    if not io.shape(autof_file) == target_auto_shape:
        print("\nCropping autofluorescence data channel to specified dimensions...\n")
        if not janky_tiff:
            autof_data = np.load(autof_file)
        autof_data = autof_data[auto_x_min:auto_x_max, auto_y_min:auto_y_max, auto_z_min:auto_z_max]
        io.convert(autof_data, autof_file, processes=32, verbose=True)
        if save_crop:
            io.convert(autof_data, os.path.join(directory, 'autof.tif'), processes=32, verbose=True)
        del autof_data

    ws.update(raw='cfos.npy', autofluorescence='autof.npy', stitched='cfos.npy')

    
    # PRE-PROCESSING RAW DATA
    preprocessed_data = os.path.join(directory, 'cfos_preproc.npy')

    if not os.path.exists(preprocessed_data):
        print("Pre-processing images...")
        new_cfos, m_thresh, s_thresh = preproc(ws.source('raw'), processes=32, thresholding=auto_thresh, maxima_threshold=m_thresh, shape_threshold=s_thresh)        
        
        print("Pre-processing finished, writing new array file...")
        io.convert(new_cfos, preprocessed_data, processes=32, verbose=True)
        print("Done.")

        if save_preproc:
            print("Saving as tif...")
            io.convert(new_cfos, os.path.join(directory, 'cfos_preproc.tif'), processes=32, verbose=True)
            print("Done.")

        del new_cfos
            
    ws.info()
    ws.debug = False

    # PREPARING FILES

    resources_directory = settings.resources_path

    annotation_file, reference_file, distance_file=ano.prepare_annotation_files(
        slicing=(slice(atlas_x_min,atlas_x_max),slice(atlas_y_min,atlas_y_max),slice(atlas_z_min,atlas_z_max)), orientation=(x_orient,y_orient,z_orient),
        overwrite=False, verbose=True);

    align_channels_affine_file   = io.join(resources_directory, 'Alignment/align_affine.txt')
    align_reference_affine_file  = io.join(resources_directory, 'Alignment/align_affine.txt')
    align_reference_bspline_file = io.join(resources_directory, 'Alignment/align_bspline.txt')
    
    if checkpoints:
        print("\nATLAS CHECKPOINT")
        print("\nNavigate to ClearMap/Resources/Atlas and ensure the newly generated reference atlas matches the orientation and crop of your experimental data.")
        checkpoint()
    
    align_channel_outdir = os.path.join(directory, 'elastix_raw_to_auto')
    align_reference_outdir = os.path.join(directory, 'elastix_auto_to_reference')
    
    if not skip_registration:
        print("\nResampling and aligning channels...\n")
        resample_parameter = {
            "source_resolution" : (raw_x_res,raw_y_res,raw_z_res),
            "sink_resolution"   : (25,25,25),
            "processes" : 32,
            "verbose" : True,             
            };    
    
        io.delete_file(ws.filename('resampled'))
    
        res.resample(ws.filename('stitched'), sink=ws.filename('resampled'), **resample_parameter)
    
        resample_parameter_auto = {
            "source_resolution" : (autof_x_res,autof_y_res,autof_z_res),
            "sink_resolution"   : (25,25,25),
            "processes" : 32,
            "verbose" : True,                
            };   
    
        res.resample(ws.filename('autofluorescence'), sink=ws.filename('resampled', postfix='autofluorescence'), **resample_parameter_auto)
    
        # Align autofluorescent image to cfos image
        align_channels_parameter = {            
            "processes" : 64,
            "moving_image" : ws.filename('resampled', postfix='autofluorescence'),
            "fixed_image"  : ws.filename('resampled'),
            "affine_parameter_file"  : align_channels_affine_file,
            "bspline_parameter_file" : None,
            "result_directory" : align_channel_outdir
            }; 
    
        elx.align(**align_channels_parameter)
    
        # Align reference image to autfluorescent image
        align_reference_parameter = {            
            "processes" : 64,
            "moving_image" : reference_file,
            "fixed_image"  : ws.filename('resampled', postfix='autofluorescence'),
            "affine_parameter_file"  :  align_reference_affine_file,
            "bspline_parameter_file" :  align_reference_bspline_file,
            "result_directory" : align_reference_outdir
            };
    
        elx.align(**align_reference_parameter)

        if checkpoints:
            print("\nALIGNMENT CHECKPOINT")
            print("\nFrom the newly generated files in your experimental directory, compare: ")
            print("\t - raw data to elastix_raw_to_auto/result.0.mhd")
            print("\t - autofluorescence data to elastix_auto_to_reference/result.1.mhd")
            print("Ensure the files are properly aligned in shape and slicing")
            checkpoint()

    if not skip_detection:
        # Setup cell detection parameters
        print("\nDetecting cells...\n")
        cell_detection_parameter = cells.default_cell_detection_parameter.copy()
        
        cell_detection_parameter['illumination_correction'] = None
        cell_detection_parameter['background_correction'] = None
        cell_detection_parameter['equalization'] = None
        cell_detection_parameter['dog_filter'] = None
        
        cell_detection_parameter['maxima_detection']['shape'] = m_shape
        cell_detection_parameter['maxima_detection']['threshold'] = m_thresh
        cell_detection_parameter['maxima_detection']['valid'] = True
        cell_detection_parameter['maxima_detection']['save'] = m_save
        
        cell_detection_parameter['shape_detection']['threshold'] = s_thresh
        cell_detection_parameter['shape_detection']['save'] = s_save
                
        cell_detection_parameter['intensity_detection']['method'] = intensity_method
        cell_detection_parameter['intensity_detection']['shape'] = intensity_shape
        cell_detection_parameter['intensity_detection']['measure'] = ['source']
        
        # cell_detection_parameter['illumination_correction']['flatfield'] = illumination_flatfield
        # cell_detection_parameter['illumination_correction']['background'] = illumination_background
        # cell_detection_parameter['illumination_correction']['scaling'] = illumination_scaling
        # cell_detection_parameter['illumination_correction']['save'] = illumination_save
        # cell_detection_parameter['background_correction']['shape'] = b_shape
        # cell_detection_parameter['background_correction']['form'] = b_form
        # cell_detection_parameter['background_correction']['save'] = b_save
        # cell_detection_parameter['equalization']['percentile'] = e_percentile
        # cell_detection_parameter['equalization']['max_value'] = e_max_value
        # cell_detection_parameter['equalization']['selem'] = e_selem
        # cell_detection_parameter['equalization']['spacing'] = e_spacing
        # cell_detection_parameter['equalization']['interpolate'] = e_interpolate
        # cell_detection_parameter['equalization']['save'] = e_save
        # cell_detection_parameter['dog_filter']['shape'] = d_shape
        # cell_detection_parameter['dog_filter']['sigma'] = d_sigma
        # cell_detection_parameter['dog_filter']['sigma2'] = d_sigma2
        # cell_detection_parameter['dog_filter']['save'] = d_save
            
        processing_parameter = cells.default_cell_detection_processing_parameter.copy()
        processing_parameter.update(
            processes = 12,
            size_max = 45,
            size_min = 20,
            overlap  = 10,
            verbose = True
            )

        ws.update(raw='cfos_preproc.npy', autofluorescence='autof.npy', stitched='cfos_preproc.npy')
        ws.info()
        ws.debug = False
        
        # Perform cell detection on cfos image
        cells.detect_cells(ws.filename('stitched'), ws.filename('cells', postfix='raw'),
                           cell_detection_parameter=cell_detection_parameter, 
                           processing_parameter=processing_parameter)  
            
        if checkpoints:
            print("\nCell detection complete!")
            checkpoint()        

        # Filter cells for size and intensity
        print("\nFiltering cells...\n")
    
        source = ws.source('cells', postfix='raw')
    
        thresholds = {
            'source' : (filter_intensity_min, filter_intensity_max),
            'size': (filter_size_min, filter_size_max)
            }
    
        cells.filter_cells(source = ws.filename('cells', postfix='raw'), 
                           sink = ws.filename('cells', postfix='filtered'), 
                           thresholds=thresholds); 


    print("\nMapping detected cells to brain regions...\n")
    
    source = ws.source('cells', postfix='filtered')
    coordinates = np.array([source[c] for c in 'xyz']).T

    coordinates_transformed = transformation(coordinates, align_channel_outdir, align_reference_outdir, workspace=ws)
    
    for f in [cfos_file, autof_file, preprocessed_data]:
        if os.path.exists(f):
            os.remove(f)
    
    # Annotate cells based on position in annotation image
    print("\nLabeling cells...\n")
    label = ano.label_points(coordinates_transformed, key='order', annotation_file=annotation_file)
    names = ano.convert_label(label, key='order', value='name')
    ID = ano.convert_label(label, key='order', value='id')
    parent_ID = ano.convert_label(label, key='order', value='parent_structure_id')

    coordinates_transformed.dtype=[(t,float) for t in ('xt','yt','zt')]
    label = np.array(label, dtype=[('order', int)])
    names = np.array(names, dtype=[('name', 'U256')])
    ID = np.array(ID, dtype=[('id', int)])
    parent_ID = np.array(parent_ID, dtype=[('parent_structure_id', 'U256')])

    import numpy.lib.recfunctions as rfn

    # Assemble cell information into NumPy array
    cells_data = rfn.merge_arrays([source[:], coordinates_transformed, label, ID, parent_ID, names], flatten=True, usemask=False)

    io.write(ws.filename('cells'), cells_data)
    
    if checkpoints:
        print("\nCell annotation complete!")
        checkpoint()

    # Remove invalid and overlapping cells. Export corrected cell data to CSV
    print("\nRemoving invalid cells and exporting detected cell data...\n")
    source = ws.source('cells')
    header = ', '.join([h for h in source.dtype.names])
    source = remove_universe(source.array)
    source = np.flip(np.sort(source, order=['source']),axis=0)
    source = remove_overlap(source, filter_distance_min) 
    source = np.sort(source, order=['z'])
    np.savetxt(ws.filename('cells', extension='csv'), source, header=header, delimiter=',', fmt='%s')

    # Voxelize detected cells
    print("\nBeginning cell voxelization...\n")
    coordinates = np.array([source[n] for n in ['xt','yt','zt']]).T
    intensities = source['source']
    
    voxelization_parameter = dict(
          shape = io.shape(annotation_file), 
          dtype = None, 
          weights = None,
          method = 'sphere', 
          radius = (3,3,3), 
          kernel = None, 
          processes = 16, 
          verbose = True
          )

    vox.voxelize(coordinates, sink=ws.filename('density', postfix='counts'), **voxelization_parameter)

    # Obtain and export region-specific detection results
    print("\nProcessing cell count results and registering annotation files...\n")
    
    num_regions, region_names, region_acronyms, region_ids, region_parent_ids, region_children = get_region_info(os.path.join(clearmap_path, 'ClearMap/Resources/Atlas/annotations_reform.json'))
    
    register_annotation(directory, annotation_file)
    
    region_counts, region_volumes, region_densities = get_region_stats(num_regions, directory, region_ids, region_parent_ids, [25,25,25])
    
    print("\nExporting cell count statistics...\n")
    
    export_regions(num_regions, region_names, region_acronyms, region_ids, region_parent_ids, region_children, region_volumes, region_counts, region_densities, directory)

    if os.path.exists(ws.filename('cells', postfix='raw')):
        os.remove(ws.filename('cells', postfix='raw'))

    with open(os.path.join(directory, 'thresholds.txt'), "w") as f:
        f.write(f"Maxima detection threshold: {m_thresh}\nShape detection threshold: {s_thresh}\n")
        
    move_files(directory, ['cells.csv', yml_file, 'region_data.mat', 'regions.csv', 'density_counts.tif', 'thresholds.txt'])

    print("CellMap Pipeline Complete!")
