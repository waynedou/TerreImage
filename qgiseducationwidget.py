# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QGISEducationDialog
                                 A QGIS plugin
 QGISEducation
                             -------------------
        begin                : 2014-04-30
        copyright            : (C) 2014 by CNES
        email                : alexia.mondot@c-s.fr
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

from PyQt4 import QtCore, QtGui
from ui_qgiseducation import Ui_QGISEducation
# create the dialog for zoom to point
import OTBApplications
from qgis.gui import QgsRubberBand, QgsMapToolPan

from qgis.core import QGis, QgsPoint, QgsRaster


from working_layer import WorkingLayer
from terre_image_task import TerreImageProcessing
from terre_image_task import TerreImageDisplay
import terre_image_utils

from processing_manager import ProcessingManager


import datetime
import os
from ptmaptool import ProfiletoolMapTool
from valuetool.valuewidget import ValueWidget

from spectral_angle import SpectralAngle

from DockableMirrorMap.dockableMirrorMapPlugin import DockableMirrorMapPlugin

class QGISEducationWidget(QtGui.QWidget, Ui_QGISEducation):
    def __init__(self, iface):
        
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
                
        QtGui.QWidget.__init__(self)
        self.setupUi(self)
        self.setupUi_extra()
        
        self.qgis_education_manager = ProcessingManager( self.iface )
        
        #self.value_tool = ValueWidget( self.iface, self )
        
        self.layer = None
        
        self.mirror_map_tool = DockableMirrorMapPlugin(self.iface)
        self.mirror_map_tool.initGui()
        
        self.angle_tool = SpectralAngle(self.iface, self.qgis_education_manager.working_directory, self.layer)


     
    def setupUi_extra(self):
        """
        Initialize the interface
        """
        
        itemProcessing = [ "", "NDVI", "NDTI", "Indice de brillance", "Angle Spectral" ]
        for index in range(len(itemProcessing)):
            item = itemProcessing[index]
            self.comboBox_processing.insertItem ( index, item )
        self.comboBox_processing.currentIndexChanged[str].connect(self.do_manage_processing)
            
        
        
        self.pushButton_working_layer.hide()
        self.label.hide()
        self.label_working_layer.hide()
        self.groupBox.hide()
        self.pushButton_brightness.hide()
        self.pushButton_ndti.hide()
        self.pushButton_ndvi.hide()
        self.pushButton_angle.hide()
        

        self.pushButton_kmeans.clicked.connect(self.kmeans)
        
        
    def do_manage_processing(self, text_changed):
        print "self.layer", self.layer
        my_processing = TerreImageProcessing( self.iface, self.qgis_education_manager.working_directory, self.layer, self.mirror_map_tool, text_changed )
        self.qgis_education_manager.add_processing(my_processing)
        self.comboBox_processing.setCurrentIndex( 0 )
        
        
    def set_comboBox_sprectral_band_display( self ):
        if self.layer:
            bands = self.layer.bands
            corres = { 'red':"Afficher la bande rouge", 'green':"Afficher la bande verte", 'blue':"Afficher la bande bleue", 'pir':"Afficher la bande pir", 'mir':"Afficher la bande mir" }
        
            self.comboBox_sprectral_band_display.clear()
            self.comboBox_sprectral_band_display.insertItem( 0, "" )
            
            if bands['red'] != 0 and bands['green'] != 0 and bands['blue'] != 0:
                print "couleurs naturelles"
                self.comboBox_sprectral_band_display.insertItem( 1, "Afficher en couleurs naturelles" )
            
            for i in range(self.layer.get_band_number()):
                y=[x for x in bands if bands[x]==i+1]
                if y :
                    text = corres[y[0]]
                    self.comboBox_sprectral_band_display.insertItem( i+2, text )
            self.comboBox_sprectral_band_display.currentIndexChanged[str].connect(self.do_manage_sprectral_band_display)
            
            
    def do_manage_sprectral_band_display(self, text_changed):
        band_to_display = None
        corres = { 'nat':"Afficher en couleurs naturelles", 'red':"Afficher la bande rouge", 'green':"Afficher la bande verte", 'blue':"Afficher la bande bleue", 'pir':"Afficher la bande pir", 'mir':"Afficher la bande mir" }
        for key in corres:
            if corres[key] == text_changed :
                who = key
                #band_to_display = self.layer.bands[key]
                #manage_QGIS.display_one_band(self.layer, who, self.iface)
                my_processing = TerreImageDisplay( self.iface, self.qgis_education_manager.working_directory, self.layer, self.mirror_map_tool, who )
                self.qgis_education_manager.add_processing(my_processing)
                break
        self.comboBox_sprectral_band_display.setCurrentIndex( 0 )
             
                 
    def kmeans(self):
        
        if self.layer == None :
            print "Aucune layer selectionnée"
        else :
            nb_class = self.spinBox_kmeans.value()
            print "nb_colass from spinbox", nb_class
            my_processing = TerreImageProcessing( self.iface, self.qgis_education_manager.working_directory, self.layer, "KMEANS", nb_class )
            #terre_image_processing.kmeans(self.layer, self.qgis_education_manager.working_directory, self.iface, nb_class)
        
        
    def working_layer(self):
        self.layer = terre_image_utils.working_layer(self.canvas)
        if self.layer:
            self.label_working_layer.setText(self.layer.name())
            
        
    
    def spectral_angles( self ):
        self.angle_tool.get_point_for_angles(self.layer)

   
        
        
    def disconnectP(self):
        """
        Disconnection of signals, go back to the main interface
        """
        #self.changeActive(False)
        #QtCore.QObject.disconnect(self.canvas, SIGNAL( "keyPressed( QKeyEvent * )" ), self.pauseDisplay )
        self.iface.mainWindow().statusBar().showMessage( "" ) 
