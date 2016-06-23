# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QGISEducation
                                 A QGIS plugin
 QGISEducation
                              -------------------
        begin               : 2016-06-02
        copyright           : (C) 2016 by CNES
        email               : alexia.mondot@c-s.fr
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
from terre_image_run_process import TerreImageProcess

# import logging for debug messages
import logging
logging.basicConfig()
# create logger
logger = logging.getLogger('TerreImage_GDALSystem')
logger.setLevel(logging.INFO)

def unionPolygonsWithOGR(filenames, outputDirectory):
    """
    Build up the union of all the geometries of the given masks.

    Keyword arguments:
        filenames -- list of masks filenames
    """
    outputFilename = os.path.join(outputDirectory, "vectorMerged.shp")
    indexClass=1
    for f in filenames:
        base = os.path.basename(os.path.splitext(f)[0])
        #Add class
        command = 'ogrinfo {} -sql "ALTER TABLE {} ADD COLUMN CLASS numeric(15)"'.format(f, base)
        os.system(command)
        command = 'ogrinfo {} -dialect SQLite -sql "UPDATE {} SET CLASS = {}"'.format(f, base, indexClass)
        os.system(command)
        #Add Label
        command = 'ogrinfo {} -sql "ALTER TABLE {} ADD COLUMN Label character(15)"'.format(f, base)
        os.system(command)
        command = 'ogrinfo {} -dialect SQLite -sql "UPDATE {} SET Label = \'{}\'"'.format(f, base, base)
        os.system(command)
        #update output
        command = 'ogr2ogr -update -append {} {}'.format(outputFilename, f)
        os.system(command)
        indexClass+=1


def compute_overviews(filename):
    """
    Runs gdaladdo on the given filename
    """
    if not os.path.isfile(filename + ".ovr"):
        command = "gdaladdo "
        command += " -ro "
        command += "\"" + filename + "\""
        command += " 2 4 8 16"
        logger.debug("command to run" + command)
        TerreImageProcess().run_process(command)

