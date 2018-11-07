# -*- coding: utf-8 -*-
"""
/***************************************************************************
 hydronet_check_and_flip
 A QGIS plugin
 Checks the hydro-network from the outfall and flip the arcs if necessary
                              -------------------
        begin               : 2018-09-18
        copyright           : (C) 2018 by Jeronimo Carranza / asterionat.com
        email               : jeronimo.carranza@asterionat.com

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
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QAction
from builtins import object

# Initialize Qt resources from file resources_qrc.py
from .resources_qrc import *
import os.path
# Import QGIS functions
from qgis.core import *
import qgis.utils
from qgis.gui import *


# Global lists
checked = []
tocheck = []
fliped = []


class hydronet_check_and_flip(object):
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'hydronet_check_and_flip_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        # self.dlg = hydronet_check_and_flipDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Hydronet Check & Flip')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'hydronet_check_and_flip')
        self.toolbar.setObjectName(u'hydronet_check_and_flip')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('hydronet_check_and_flip', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.iface.addVectorToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToVectorMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/hydronet_check_and_flip/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Hydronet Check and Flip.\nYou must have selected the outfalls arcs in the active layer. '),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Hydronet Check and Flip'),
                action)
            self.iface.removeVectorToolBarIcon(action)


    def run(self):
        """Run method that performs all the real work
        """
        layer = qgis.utils.iface.mapCanvas().currentLayer()

        if layer is None:
            qgis.utils.iface.messageBar().pushMessage(u"Hydronet Check and Flip ", u"No selected layer", level=Qgis.Critical)
            return

        if layer.geometryType() != QgsWkbTypes.LineGeometry:
            qgis.utils.iface.messageBar().pushMessage(u"Hydronet Check and Flip ", u"The selected layer is not a line layer", level=Qgis.Critical)
            return

        if layer.selectedFeatures() == []:
            qgis.utils.iface.messageBar().pushMessage(u"Hydronet Check and Flip ", u"No selected outfall arcs", level=Qgis.Critical)
            return

        """ Outfalls """
        outfalls = layer.selectedFeatures()
        QgsMessageLog.logMessage('Outfalls: '+str(outfalls)[1:-1],'Hydronet Check and Flip', Qgis.Info)

        """ Spatial index """
        index = QgsSpatialIndex(layer.getFeatures())

        global tocheck
        global checked
        global fliped

        """ Checking for each outfall """
        for feature in outfalls:
            checked.append(feature.id())
            self.checkarc(feature, index, layer)

        """ Check the updated list 'tocheck' """
        n = 0
        while(n <= len(layer) and len(tocheck) > 0):
            checked.append(tocheck[0])
            arc = [feat for feat in layer.getFeatures() if feat.id() == tocheck[0]]
            self.checkarc(arc[0], index, layer)
            tocheck = [x for x in set(tocheck) if x not in set(checked)]
            n = n + 1

        """ Finishing """
        QgsMessageLog.logMessage('Fliped Arcs:: '+str(fliped)[1:-1],'Hydronet Check and Flip', Qgis.Info)
        QgsMessageLog.logMessage('Checked Arcs:: '+str(checked)[1:-1],'Hydronet Check and Flip', Qgis.Info)
        #layer.commitChanges()
        #layer.removeSelection()
        #qgis.utils.iface.mainWindow().findChild(QAction, 'mActionToggleEditing').trigger() 
        qgis.utils.iface.mapCanvas().refresh()
        tocheck = []
        checked = []
        fliped = []


    def checkarc(self, arc, index, layer):
        global tocheck
        global checked
        global fliped
        uparcs_idx = self.arclist(arc, index, layer, 0)
        dwarcs_idx = self.arclist(arc, index, layer, -1)
        # QgsMessageLog.logMessage('Checking Arc: '+str(arc.id())+' Up: '+str(uparcs_idx)[1:-1]+' Dw: '+str(dwarcs_idx)[1:-1],'Hydronet Check and Flip', Qgis.Info)
        if (self.anyin(uparcs_idx, checked)):
            self.flip(arc, layer)
            tocheck.extend(dwarcs_idx)
            fliped.append(arc.id())
        else:
            tocheck.extend(uparcs_idx)


    def arclist(self, arc, index, layer, op):
        delta = 0.000001
        geom = arc.geometry()
        if geom.isMultipart():
            multi_geom = geom.asMultiPolyline()
            opnode = multi_geom[op][op]
        else:
            nodes = geom.asPolyline()
            opnode = nodes[op]
        opnode_rectangle = QgsRectangle(opnode.x()-delta, opnode.y()-delta, opnode.x()+delta, opnode.y()+delta)
        oparcs_idx = index.intersects(opnode_rectangle)
        oparcs_idx.remove(arc.id())
        return(oparcs_idx)


    def flip(self, arc, layer):
        QgsMessageLog.logMessage('Fliping Arc : '+str(arc.id()),'Hydronet Check and Flip', Qgis.Info)
        layer.startEditing()
        layer.beginEditCommand( "Fliping" )
        geom = arc.geometry()
        if geom.isMultipart():
            multi = QgsMultiLineString()
            for line in geom.asGeometryCollection():
                multi.addGeometry(line.constGet().reversed())
            revgeom = QgsGeometry(multi)
            layer.changeGeometry(arc.id(),revgeom)
        else:
            revgeom = QgsGeometry(geom.constGet().reversed())
            layer.changeGeometry(arc.id(),revgeom)
        layer.endEditCommand()


    def anyin(self, xlist, ylist):
        for xi in xlist:
            if (xi in ylist):
                return(True)
                break
        return(False)

