#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CellMapHPC
=======

This script is the main pipeline to analyze immediate early gene expression 
data from iDISCO+ cleared tissue [Renier2016]_.

See the :ref:`CellMap tutorial </CellMap.ipynb>` for a tutorial and usage.


.. image:: ../Static/cell_abstract_2016.jpg
   :target: https://doi.org/10.1016/j.cell.2020.01.028
   :width: 300

.. figure:: ../Static/CellMap_pipeline.png

  iDISCO+ and ClearMap: A Pipeline for Cell Detection, Registration, and 
  Mapping in Intact Samples Using Light Sheet Microscopy.


References
----------
.. [Renier2016] `Mapping of brain activity by automated volume analysis of immediate early genes. Renier* N, Adams* EL, Kirst* C, Wu* Z, et al. Cell. 2016 165(7):1789-802 <https://doi.org/10.1016/j.cell.2016.05.007>`_
"""
__author__    = 'Christoph Kirst <christoph.kirst.ck@gmail.com>'
__license__   = 'GPLv3 - GNU General Pulic License v3 (see LICENSE)'
__copyright__ = 'Copyright © 2020 by Christoph Kirst'
__webpage__   = 'http://idisco.info'
__download__  = 'http://www.github.com/ChristophKirst/ClearMap2'

if __name__ == "__main__":
     
    #%%############################################################################
    ### Initialization 
    ###############################################################################

    #%% Initialize workspace
    import sys
    sys.path.append('/home/npoleksic/ClearMap2-HPC') # CONFIGURE PATH TO CLEARMAP
    from ClearMap.Environment import *  #analysis:ignore

    #directories and files
    directory = '/home/npoleksic/LSS/ncb-core/users/npoleksic/sarah_data_new_hpc' # CONFIGURE DATA DIRECTORY PATH
    expression_raw      = 'cfos/16-09-36_TR1 640_UltraII_C00_xyz-Table Z<Z,4>.ome.tif' # CONFIGURE RAW DATA PATH FROM DIRECTORY
    expression_auto     = 'autof/15-12-07_TR1 autofluo_UltraII_C00_xyz-Table Z<Z,4>.ome.tif' # CONFIGURE AUTOF DATA PATH FROM DIRECTORY

    ws = wsp.Workspace('CellMap', directory=directory);
    ws.update(raw=expression_raw, autofluorescence=expression_auto)
    ws.info()

    ws.debug = False

    resources_directory = settings.resources_path

    #%% Initialize alignment 

    #init atals and reference files
    annotation_file, reference_file, distance_file=ano.prepare_annotation_files( # CONFIGURE ATLAS ORIENTATION TO MATCH DATA
        slicing=(slice(None),slice(None),slice(100,326)), orientation=(3,1,2),
        overwrite=False, verbose=True);

    #alignment parameter files    
    align_channels_affine_file   = io.join(resources_directory, 'Alignment/align_affine.txt')
    align_reference_affine_file  = io.join(resources_directory, 'Alignment/align_affine.txt')
    align_reference_bspline_file = io.join(resources_directory, 'Alignment/align_bspline.txt')

    #%%############################################################################
    ### Data conversion
    ############################################################################### 

    #%% Convert raw data to npy file     

    source = ws.source('raw');
    sink   = ws.filename('stitched')
    io.delete_file(sink)
    io.convert(source, sink, processes=16, verbose=True);

    #%%############################################################################
    ### Resampling and atlas alignment 
    ###############################################################################

    #%% Resample 

    resample_parameter = { # CONFIGURE RESUOLUTION OF RAW DATA
        "source_resolution" : (3.77556,3.77556,3),
        "sink_resolution"   : (25,25,25),
        "processes" : 16,
        "verbose" : True,             
        };

    io.delete_file(ws.filename('resampled'))

    res.resample(ws.filename('stitched'), sink=ws.filename('resampled'), **resample_parameter)

    #%% Resample autofluorescence

    resample_parameter_auto = { # CONFIGURE RESOLUTION OF AUTOF DATA
        "source_resolution" : (3.77556,3.77556,3),
        "sink_resolution"   : (25,25,25),
        "processes" : 16,
        "verbose" : True,                
        };    

    res.resample(ws.filename('autofluorescence'), sink=ws.filename('resampled', postfix='autofluorescence'), **resample_parameter_auto)

    #%% Alignment - resampled to autofluorescence

    # align the two channels
    align_channels_parameter = {            
        #moving and reference images
        "processes" : 16,
        "moving_image" : ws.filename('resampled', postfix='autofluorescence'),
        "fixed_image"  : ws.filename('resampled'),

        #elastix parameter files for alignment
        "affine_parameter_file"  : align_channels_affine_file,
        "bspline_parameter_file" : None,

        #directory of the alignment result
        "result_directory" :  ws.filename('resampled_to_auto')
        }; 

    elx.align(**align_channels_parameter);

    #%% Alignment - autoflourescence to reference

    # align autofluorescence to reference
    align_reference_parameter = {            
        #moving and reference images
        "processes" : 16,
        "moving_image" : reference_file,
        "fixed_image"  : ws.filename('resampled', postfix='autofluorescence'),

        #elastix parameter files for alignment
        "affine_parameter_file"  :  align_reference_affine_file,
        "bspline_parameter_file" :  align_reference_bspline_file,
        #directory of the alignment result
        "result_directory" :  ws.filename('auto_to_reference')
        };

    elx.align(**align_reference_parameter);

    #%%############################################################################
    ### Create test data
    ###############################################################################

    #%% Crop test data 

    #select sublice for testing the pipeline
    # slicing = (slice(100,400),slice(1300,1600),slice(1150,1300));
    # ws.create_debug('stitched', slicing=slicing);
    # ws.debug = True;   

    #%%############################################################################
    ### Cell detection
    ###############################################################################

    #%% Cell detection:

    cell_detection_parameter = cells.default_cell_detection_parameter.copy();
    cell_detection_parameter['intensity_detection']['measure'] = ['source']; 
    # CONFIGURE CELL DETECTION PARAMETERS

    processing_parameter = cells.default_cell_detection_processing_parameter.copy();
    processing_parameter.update( # CONFIGURE PROCESSING PARAMETERS
        processes = 16, # 'serial',
        size_max = 100, #100, #35,
        size_min = 50,# 30, #30,
        overlap  = 32, #32, #10,
        verbose = True
        )

    cells.detect_cells(ws.filename('stitched'), ws.filename('cells', postfix='raw'),
                       cell_detection_parameter=cell_detection_parameter, 
                       processing_parameter=processing_parameter)  

    #%% Cell statistics

    source = ws.source('cells', postfix='raw')

    #%% Filter cells

    thresholds = {
        'source' : None,
        'size'   : (20,90) # CONFIGURE THRESHOLDS
        }

    cells.filter_cells(source = ws.filename('cells', postfix='raw'), 
                       sink = ws.filename('cells', postfix='filtered'), 
                       thresholds=thresholds); 

    #%%############################################################################
    ### Cell atlas alignment and annotation
    ###############################################################################

    #%% Cell alignment

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

    #%% Cell annotation
    ano.set_annotation_file(annotation_file)   # CONFIGURE ANNOTATION
    label = ano.label_points(coordinates_transformed, key='order');
    names = ano.convert_label(label, key='order', value='name');
    ID = ano.convert_label(label, key='order', value='id');
    acronym = ano.convert_label(label, key='order', value='acronym');  

    #%% Save results

    coordinates_transformed.dtype=[(t,float) for t in ('xt','yt','zt')]
    label = np.array(label, dtype=[('order', int)]);
    names = np.array(names, dtype=[('name', 'U256')])
    ID = np.array(ID, dtype=[('id', int)])
    acronym = np.array(acronym, dtype=[('acronym', 'U256')])

    import numpy.lib.recfunctions as rfn
    cells_data = rfn.merge_arrays([source[:], coordinates_transformed, label, ID, acronym, names,], flatten=True, usemask=False)

    io.write(ws.filename('cells'), cells_data)

    #%%############################################################################
    ### Cell csv generation for external analysis
    ###############################################################################

    #%% CSV export

    source = ws.source('cells');
    header = ', '.join([h for h in source.dtype.names]);
    np.savetxt(ws.filename('cells', extension='csv'), source[:], header=header, delimiter=',', fmt='%s')

    #%% ClearMap 1.0 export

    source = ws.source('cells');

    clearmap1_format = {'points' : ['x', 'y', 'z'], 
                        'points_transformed' : ['xt', 'yt', 'zt'],
                        'intensities' : ['source', 'dog', 'background', 'size']}

    for filename, names in clearmap1_format.items():
        sink = ws.filename('cells', postfix=['ClearMap1', filename]);
        data = np.array([source[name] if name in source.dtype.names else np.full(source.shape[0], np.nan) for name in names]);
        io.write(sink, data);

    #%%############################################################################
    ### Voxelization - cell density
    ###############################################################################

    source = ws.source('cells')

    coordinates = np.array([source[n] for n in ['xt','yt','zt']]).T;
    intensities = source['source'];

    #%% Unweighted 

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

    #%% Weighted 

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