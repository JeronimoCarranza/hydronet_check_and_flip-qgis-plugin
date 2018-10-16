# -*- coding: utf-8 -*-
"""
/***************************************************************************
 hydronet_check_and_flip
 A QGIS plugin
 Checks the hydro-network from the outfall & flip the arcs if necessary
                             -------------------
        begin                : 2018-09-18
        copyright            : (C) 2018 by Jeronimo Carranza / asterionat.com
        email                : jeronimo.carranza@asterionat.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load hydronetCheckFlip class from file hydronet_check_and_flip.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .hydronet_check_and_flip import hydronet_check_and_flip
    return hydronet_check_and_flip(iface)
