
layer = qgis.utils.iface.mapCanvas().currentLayer()
outfalls = layer.selectedFeatures()
QgsMessageLog.logMessage('Outfalls: '+str(len(outfalls)),'Hydronet Check and Flip', Qgis.Info)
if (layer.dataProvider().fieldNameIndex('HYNCHECK') == -1): 
    layer.startEditing()
    layer.dataProvider().addAttributes([QgsField( 'HYNCHECK', QVariant.Int)])
    layer.updateFields()
    for f in layer.getFeatures():
        f['HYNCHECK'] = 0
        layer.updateFeature( f )        
    layer.commitChanges()

index = QgsSpatialIndex(layer.getFeatures())

arc = outfalls[0]

delta = 0.000001
geom = arc.geometry()
if geom.isMultipart():
    multi_geom = geom.asMultiPolyline()
    upnode = multi_geom[0][0]
    dwnode = multi_geom[-1][-1]
else:
    nodes = geom.asPolyline()
    upnode = nodes[0]
    dwnode = nodes[-1]

upnode_rectangle = QgsRectangle(upnode.x()-delta, upnode.y()-delta, upnode.x()+delta, upnode.y()+delta)
uparcs_idx = index.intersects(upnode_rectangle)
uparcs_idx.remove(arc.id())

QgsMessageLog.logMessage('UpArcs Idx: '+str(len(uparcs_idx)),'Hydronet Check and Flip', Qgis.Info)

uparcs = layer.getFeatures(uparcs_idx) 
#QgsMessageLog.logMessage('UpArcs '+uparcs,'Hydronet Check and Flip', Qgis.Info)

layer.startEditing()
arc["HYNCHECK"] = 1
layer.updateFeature( arc )
layer.commitChanges()

for uparc in uparcs:
    QgsMessageLog.logMessage('PreChecking UpArc '+str(uparc.id()),'Hydronet Check and Flip', Qgis.Info)


