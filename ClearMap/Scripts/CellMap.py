#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CellMap
=======

Adapted original ClearMap2.0 CellMap.py script to be executed from a shell script with YAML configuration file

"""
__license__   = 'GPLv3 - GNU General Pulic License v3 (see LICENSE)'
__copyright__ = 'Copyright © 2020 by Christoph Kirst'

from utils import *

if __name__ == "__main__":
    
    # Verify that script is run correctly from terminal
    if len(sys.argv) < 1:
        print("ERROR: SYSTEM ARG COUNT")
        sys.exit()
    clearmap_path = sys.argv[1]
    # clearmap_path = '/home/npoleksic/ClearMap2-HPC'

    sys.path.append(clearmap_path)
    # clearmap_path = '/home/npoleksic/ClearMap2-HPC'
    # Import supplementary ClearMap modules
    from ClearMap.Environment import *

    # yml_file = 'config_parameters_paul.yml'
    yml_file = 'config_parameters_ga2.yml'
    # yml_file = os.path.join(clearmap_path, yml_file)
    # Read parameters from YML file
    config = read_config(yml_file)

    if config:
        directory = config.get('experiment_path')
        shutil.copy(yml_file, directory)

        ws = wsp.Workspace('CellMap', directory=directory)

        filetype = config.get('file_type')
        if filetype == "tiff_folder" or filetype == "npy":
            expression_raw = config.get('raw_data_path')
            expression_auto = config.get('autof_data_path')
        # elif filetype == "npy":

        #     raw_file = config.get('raw_data_path');
        #     cfos_npy = np.load(os.path.join(directory, raw_file));
        #     filtered_cfos = np.empty(cfos_npy.shape, dtype=cfos_npy.dtype);
        #     for z in range(cfos_npy.shape[2]):
        #         filtered_cfos[:,:,z] = cfos_npy[:,:,z] - np.minimum(cfos_npy[:,:,z], cv2.GaussianBlur(cfos_npy[:,:,z], (0,0), 5));
        #         print("Gaussian filtering slice: " + str(z))

        #     np.save(os.path.join(directory, "cfos_conv1.npy"), filtered_cfos)
        #     expression_raw = "cfos_conv1.npy"
        #     expression_auto = config.get('autof_data_path')
        elif filetype == "tiff":
            raw_fn = config.get('raw_data_path')
            autof_fn = config.get('autof_data_path')
            
            expression_raw = raw_fn.split('.')[0] + '.npy'
            expression_auto = autof_fn.split('.')[0] + '.npy'
            
            print("\nConverting input files to .npy ...\n")

            cfos_tiff = os.path.join(directory, raw_fn)
            autof_tiff = os.path.join(directory, autof_fn)

            cfos_npy = np.transpose(tiff.imread(cfos_tiff), (2,1,0))
            filtered_cfos = np.empty(cfos_npy.shape, dtype=cfos_npy.dtype);
            for z in range(cfos_npy.shape[2]):
                filtered_cfos[:,:,z] = cfos_npy[:,:,z] - np.minimum(cfos_npy[:,:,z], cv2.GaussianBlur(cfos_npy[:,:,z], (0,0), 5));
                print("Gaussian filtering slice: " + str(z))
                
                
            np.save(os.path.join(directory, expression_raw), filtered_cfos)
            # np.save(os.path.join(directory, expression_raw), np.transpose(tiff.imread(cfos_tiff), (2,1,0)))
            np.save(os.path.join(directory, expression_auto), np.transpose(tiff.imread(autof_tiff), (2,1,0)))


        
        target_raw_shape = io.shape(os.path.join(directory, expression_raw))
        target_auto_shape = io.shape(os.path.join(directory, expression_auto))

        save_preproc = config.get('save_preprocessing')
        skip_registration = config.get('skip_registration')
        skip_detection = config.get('skip_detection')
        
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
            
        illumination = config.get('illumination_correction')
        illumination_flatfield = config.get('illumination_correction_flatfield')
        illumination_background = config.get('illumination_correction_background')
        illumination_scaling = config.get('illumination_correction_scaling')
        illumination_save = config.get('illumination_correction_save')
        
        if not illumination_flatfield:
            illumination_flatfield = None
        else:
            illumination_flatfield = os.path.join(directory, illumination_flatfield)
        if not illumination_background:
            illumination_background = None
        else:
            illumination_background = os.path.join(directory, illumination_background)
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
            intensity_measure = ['source']
        
        filter_size_min = config.get('filter_size_min')
        filter_size_max = config.get('filter_size_max')
        filter_intensity_min = config.get('filter_intensity_min')
        filter_intensity_max = config.get('filter_intensity_max')
        filter_distance_min = config.get('filter_distance_min')
        
        if(filter_size_max == "MAX"):
            filter_size_max = None
        if(filter_intensity_max == "MAX"):
            filter_intensity_max = None
            

    # Initialize experimental environment
    cfos = os.path.join(directory, 'cfos.npy')
    autof = os.path.join(directory, 'autof.npy')
    
    if not os.path.exists(cfos):
        print("\nConverting raw data channel to npy array...\n")
        io.convert(os.path.join(directory, expression_raw), cfos, processes=32, verbose=True)

    if not os.path.exists(autof):
        print("\nConverting autofluorescence data channel to npy array...\n")
        io.convert(os.path.join(directory, expression_auto), autof, processes=32, verbose=True)

    ws.update(raw='cfos.npy', autofluorescence='autof.npy', stitched='cfos.npy')
    ws.debug = False

    if not io.shape(ws.source('raw')) == target_raw_shape:
        print("\nCropping raw data channel to specified dimensions...\n")
        cfos_data = np.load(ws.filename('raw'))
        cfos_data = cfos_data[raw_x_min:raw_x_max, raw_y_min:raw_y_max, raw_z_min:raw_z_max]
        io.convert(cfos_data, cfos, processes=32, verbose=True)
        del cfos_data

    if not io.shape(ws.source('autofluorescence')) == target_auto_shape:
        print("\nCropping autofluorescence data channel to specified dimensions...\n")
        autof_data = np.load(ws.filename('autofluorescence'))
        autof_data = autof_data[auto_x_min:auto_x_max, auto_y_min:auto_y_max, auto_z_min:auto_z_max]
        io.convert(autof_data, autof, processes=32, verbose=True)
        del autof_data

    ws.update(raw='cfos.npy', autofluorescence='autof.npy', stitched='cfos.npy')

    preprocessed_data = os.path.join(directory, 'cfos_preproc.npy')
    
    if not os.path.exists(preprocessed_data)
        
    # ws.update(raw='cfos_preproc.npy', autofluorescence='autof.npy', stitched='cfos_preproc.npy')
        print("Pre-processing images...")
        new_cfos = np.empty_like(ws.source('raw'));
        kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3,3));
        for z in range(new_cfos.shape[2]):
            new_cfos[:,:,z] = ws.source('raw')[:,:,z] - np.minimum(ws.source('raw')[:,:,z], cv2.GaussianBlur(ws.source('raw')[:,:,z], (0,0), 10));
            new_cfos[:,:,z] = cv2.morphologyEx(new_cfos[:,:,z], cv2.MORPH_OPEN, kernel);
            print(f"Filtered slice: {z}")

        print("Pre-processing finished, writing new array file...")
        io.convert(new_cfos, preprocessed_data, processes=32, verbose=True)
        print("Done.")

        if save_preproc:
            print("Saving as tif...")
            io.convert(new_cfos, os.path.join(directory, 'cfos_preproc.tif'), processes=32, verbose=True)
            print("Done.")

        ws.update(raw='cfos_preproc.npy', autofluorescence='autof.npy', stitched='cfos_preproc.npy')
            
    ws.info()
    ws.debug = False

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
        print("\nDetecting cells...\n")
        # Setup cell detection parameters
        cell_detection_parameter = cells.default_cell_detection_parameter.copy()
    
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
            
        processing_parameter = cells.default_cell_detection_processing_parameter.copy()
        processing_parameter.update(
            processes = 12,
            size_max = 45,
            size_min = 20,
            overlap  = 10,
            verbose = True
            )
    
        # Perform cell detection on cfos image
        cells.detect_cells(ws.filename('stitched'), ws.filename('cells', postfix='raw'),
                           cell_detection_parameter=cell_detection_parameter, 
                           processing_parameter=processing_parameter)  
        
        if checkpoints:
            print("\nCell detection complete!")
            checkpoint()
            

    # Filter cells for size and intensity
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
    coordinates = np.array([source[c] for c in 'xyz']).T

    coordinates_transformed = transformation(coordinates, align_channel_outdir, align_reference_outdir, workspace=ws)
    
    # Annotate cells based on position in annotation image
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
        
    print("\nRemoving invalid cells and exporting detected cell data...\n")
    
    # Remove invalid and overlapping cells. Export corrected cell data to CSV
    source = ws.source('cells')
    header = ', '.join([h for h in source.dtype.names])
    source = remove_universe(source.array)
    source = np.flip(np.sort(source, order=['source']),axis=0)
    source = remove_overlap(source, filter_distance_min) 
    source = np.sort(source, order=['z'])
    np.savetxt(ws.filename('cells', extension='csv'), source, header=header, delimiter=',', fmt='%s')
    
    # np.savetxt(os.path.join(directory, 'cells_removed.csv'), source, header=header, delimiter=',', fmt='%s')
    # print("\nBeginning cell voxelization...\n")
    # Voxelize detected cells
    coordinates = np.array([source[n] for n in ['xt','yt','zt']]).T
    # intensities = source['source']
    
    # voxelization_parameter = dict(
    #       shape = io.shape(annotation_upscaled), 
    #       dtype = None, 
    #       weights = None,
    #       method = 'sphere', 
    #       radius = (3,3,3), 
    #       kernel = None, 
    #       processes = 16, 
    #       verbose = True
    #       )

    # vox.voxelize(coordinates, sink=ws.filename('density', postfix='counts'), **voxelization_parameter)
        
    print("\nProcessing cell count results and registering annotation files...\n")
    
    # Obtain and export region-specific detection results
    num_regions, region_names, region_acronyms, region_ids, region_parent_ids, region_children = get_region_info(os.path.join(clearmap_path, 'ClearMap/Resources/Atlas/annotations_reform.json'))

    register_annotation(directory, annotation_file)
    
    region_counts, region_volumes, region_densities = get_region_stats(num_regions, directory, region_ids, region_parent_ids, [25,25,25])
    
    print("\nExporting cell count statistics...\n")
    
    export_regions(num_regions, region_names, region_acronyms, region_ids, region_parent_ids, region_children, region_volumes, region_counts, region_densities, directory)

    # os.remove(ws.filename('stitched'))
    os.remove(ws.filename('cells', postfix='raw'))
    # os.remove(ws.filename('cells', postfix='filtered'))

    files_to_move = ['cells.csv', yml_file, 'region_data.mat', 'regions.csv']
    move_files(directory, files_to_move)
    
    print("CellMap Pipeline Complete!")
