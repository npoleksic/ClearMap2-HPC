# -*- coding: utf-8 -*-
"""
Environment
===========

Initialize a ClearMap environment with all main functionality.

Note
----
To initialize the main functions in a ClearMap script use:
>>> from ClearMap.Environment import *
"""
__author__    = 'Christoph Kirst <christoph.kirst.ck@gmail.com>'
__license__   = 'GPLv3 - GNU General Pulic License v3 (see LICENSE.txt)'
__copyright__ = 'Copyright © 2020 by Christoph Kirst'
__webpage__   = 'http://idisco.info'
__download__  = 'http://www.github.com/ChristophKirst/ClearMap2'

###############################################################################
### Python
###############################################################################

import sys   
import os    
import glob  

import numpy as np                
import matplotlib.pyplot as plt

from importlib import reload

###############################################################################
### ClearMap
###############################################################################

#generic
import ClearMap.Settings as settings
print("ClearMap.Settings Imported")

import ClearMap.IO.IO as io
print("ClearMap.IO.IO Imported")

import ClearMap.IO.Workspace as wsp
print("ClearMap.IO.Workspace Imported")

import ClearMap.Tests.Files as tfs 
print("ClearMap.Tests.Files Imported")

# import ClearMap.Visualization.Plot3d as p3d
import ClearMap.Visualization.Color as col
print("ClearMap.Visualization.Color Imported")

import ClearMap.Utils.TagExpression as te
print("ClearMap.Utils.TagExpression Imported")

import ClearMap.Utils.Timer as tmr
print("ClearMap.Utils.Timer Imported")

import ClearMap.ParallelProcessing.BlockProcessing as bp
print("ClearMap.ParallelProcessing.BlockProcessing Imported")

import ClearMap.ParallelProcessing.DataProcessing.ArrayProcessing as ap
print("ClearMap.ParallelProcessing.DataProcessing.ArrayProcessing Imported")

#alignment
import ClearMap.Alignment.Annotation as ano
print("ClearMap.Alignment.Annotation Imported")

import ClearMap.Alignment.Resampling as res
print("ClearMap.Alignment.Resampling Imported")

import ClearMap.Alignment.Elastix as elx
print("ClearMap.Alignment.Elastix Imported")

#image processing
import ClearMap.ImageProcessing.Clipping.Clipping as clp
print("ClearMap.ImageProcessing.Clipping.Clipping Imported")

import ClearMap.ImageProcessing.Filter.Rank as rnk
print("ClearMap.ImageProcessing.Filter.Rank Imported")

import ClearMap.ImageProcessing.Filter.StructureElement as se
print("ClearMap.ImageProcessing.Filter.StructureElement Imported")

import ClearMap.ImageProcessing.Differentiation as dif
print("ClearMap.ImageProcessing.Differentiation Imported")

#analysis
import ClearMap.Analysis.Graphs.GraphGt as grp
print("ClearMap.Analysis.Graphs.GraphGt Imported")

import ClearMap.Analysis.Graphs.GraphProcessing as gp
print("ClearMap.Analysis.Graphs.GraphProcessing Imported")

import ClearMap.Analysis.Measurements.MeasureExpression as me
print("ClearMap.Analysis.Measurements.MeasureExpression Imported")

import ClearMap.Analysis.Measurements.MeasureRadius as mr
print("ClearMap.Analysis.Measurements.MeasureRadius Imported")

import ClearMap.Analysis.Measurements.Voxelization as vox
print("ClearMap.Analysis.Measurements.Voxelization Imported")

# experts
# import ClearMap.ImageProcessing.Experts.Vasculature as vasc
import ClearMap.ImageProcessing.Experts.Cells as cells
print("ClearMap.ImageProcessing.Experts.Cells Imported")
print("Environment import complete")
###############################################################################
### All
###############################################################################

__all__ = ['sys', 'os', 'glob', 'np', 'plt', 'reload',
           'settings', 'io', 'wsp', 'tfs', 'col', 'te', 
           'tmr', 'bp', 'ap', 'ano', 'res', 'elx', 'clp', 
           'rnk', 'se', 'dif', 'grp', 'gp', 'me', 'mr', 
           'vox', 'cells'];
