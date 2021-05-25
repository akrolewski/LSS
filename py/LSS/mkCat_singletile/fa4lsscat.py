import os
import shutil
import unittest
from datetime import datetime
import json
import numpy as np
import fitsio
import desimodel

from fiberassign.targets import (TargetsAvailable)
from fiberassign.utils import option_list, GlobalTimers
from fiberassign.hardware import load_hardware
from fiberassign.tiles import load_tiles, Tiles
from fiberassign.targets import (TARGET_TYPE_SCIENCE, TARGET_TYPE_SKY,
                                 TARGET_TYPE_SUPPSKY,
                                 TARGET_TYPE_STANDARD, TARGET_TYPE_SAFE,
                                 Targets, TargetsAvailable, TargetTree,
                                 LocationsAvailable, load_target_file)
from fiberassign.assign import (Assignment, write_assignment_fits,
                                write_assignment_ascii, merge_results,
                                read_assignment_fits_tile)                                 
import desimodel.io as dmio




def getfatiles(targetf,tilef,dirout='',dt = '2020-03-10T00:00:00',faver='2.3.0'):
    '''
    will write out fiberassignment files for each tile with the FASSIGN, FTARGETS, FAVAIL HDUS
    these are what are required to determine the geometry of what fiberassign thinks could have been observed and also match to actual observations (though FASSIGN is not really necessary)
    targetf is file with all targets to be run through
    tilef lists the tiles to "assign"
    dirout is the directory where this all gets written out !make sure this is unique for every different target!
    '''                                
    tgs = Targets()
    load_target_file(tgs,targetf)
    print('loaded target file '+targetf)
    tree = TargetTree(tgs, 0.01)
    hw = load_hardware(rundate=dt)
    tiles = load_tiles(tiles_file=tilef)
    #tgsavail = TargetsAvailable(hw, tgs, tiles, tree)
    #favail = LocationsAvailable(tgsavail)
    del tree
    if faver == '2.3.0':
        tgsavail = TargetsAvailable(hw, tgs, tiles, tree)
        favail = LocationsAvailable(tgsavail)
        asgn = Assignment(tgs, tgsavail, favail)
    if faver == '2.4.0' or faver == '2.5.0' or faver == '2.5.1':
        tgsavail = TargetsAvailable(hw, tgs, tiles, tree)
        favail = LocationsAvailable(tgsavail)
        asgn = Assignment(tgs, tgsavail, favail,{}) #this is needed for fiberassign 2.4 and higher(?)
    if int(faver[:1]) >= 3:
        tile_targetids, tile_x, tile_y = targets_in_tiles(hw, tgs, tiles)
        tgsavail = TargetsAvailable(hw, tiles, tile_targetids, tile_x, tile_y)
        favail = LocationsAvailable(tgsavail)
        asgn = Assignment(tgs, tgsavail, favail,{}) #this is needed for fiberassign 2.4 and higher(?)
    
    asgn.assign_unused(TARGET_TYPE_SCIENCE)
    write_assignment_fits(tiles, asgn, out_dir=dirout, all_targets=True)
    print('wrote assignment files to '+dirout)	