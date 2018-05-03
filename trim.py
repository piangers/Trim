# -*- coding: UTF-8 -*-
from qgis.core import *
from qgis.gui import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from selectiontool import SelectionTool
import resources_rc

class Trim:

    def __init__(self, iface):
      # Save reference to the QGIS interface
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        self.active = False

    def initGui(self):
        # 1 - CRIAR UM BOTÃO PARA ATIVAR A FERRAMENTA
        settings = QSettings()
        self.trimAction = QAction(QIcon(":/plugins/Trim/tr.png"), u'Trim', self.iface.mainWindow())
        self.toolbar = self.iface.addToolBar(u'Trim tools')
        self.toolbar.addAction(self.trimAction)
        # 2 - CONECTAR O CLIQUE DO BOTÃO COM UM MÉTODO ("SLOT")
        self.trimAction.triggered.connect(self.trim)
        self.freehand_edit = \
        self.freehand_edit.setEnabled(False)
        self.freehand_edit.setCheckable(True)
        # Adiciona botão toolbar no menu 
        self.iface.digitizeToolBar().addAction(self.freehand_edit)
        self.iface.editMenu().addAction(self.freehand_edit)
        # Padrões fixados
        self.spinBox = QDoubleSpinBox(self.iface.mainWindow())
        self.spinBox.setDecimals(3)
        self.spinBox.setMinimum(0.000)
        self.spinBox.setMaximum(5.000)
        self.spinBox.setSingleStep(0.100)
        toleranceval = \
            settings.value("/freehandEdit/tolerance", 0.000, type=float)
        if not toleranceval:
            settings.setValue("/freehandEdit/tolerance", 0.000)
        self.spinBox.setValue(toleranceval)
        self.spinBoxAction = \
            self.iface.digitizeToolBar().addWidget(self.spinBox)
        self.spinBox.setToolTip("Tolerance. Level of simplification.")
        self.spinBoxAction.setEnabled(False)
        # Conecta o sinals do botão 
        self.freehand_edit.activated.connect(self.freehandediting)
        self.iface.currentLayerChanged['QgsMapLayer*'].connect(self.toggle)
        self.canvas.mapToolSet['QgsMapTool*'].connect(self.deactivate)
        self.spinBox.valueChanged[float].connect(self.tolerancesettings)
        # Get the tool
        self.tool = Trim(self.canvas)

        

    
    def deactivate(self):
        self.freehand_edit.setChecked(False)
        if self.active:
            self.tool.rbFinished['QgsGeometry*'].disconnect(self.createFeature)
        self.active = False
    
    def unload(self):
        self.iface.digitizeToolBar().removeAction(self.freehand_edit)
        self.iface.digitizeToolBar().removeAction(self.spinBoxAction)
        del self.toolbar
        try:
            self.canvas.unsetMapTool(self.seletor)
        except:
            pass

    def tolerancesettings(self):
        settings = QSettings()
        settings.setValue("/freehandEdit/tolerance", self.spinBox.value())

    def freehandediting(self):
        self.canvas.setMapTool(self.tool)
        self.freehand_edit.setChecked(True)
        self.tool.rbFinished['QgsGeometry*'].connect(self.createFeature)
        self.active = True

    def toggle(self):
        mc = self.canvas
        layer = mc.currentLayer()
        if layer is None:
            return

        #Decide whether the plugin button/menu is enabled or disabled
        if (layer.isEditable() and (layer.geometryType() == QGis.Line or
                                    layer.geometryType() == QGis.Polygon)):
            self.freehand_edit.setEnabled(True)
            self.spinBoxAction.setEnabled(
                layer.crs().projectionAcronym() != "longlat")
            try:  # remove any existing connection first
                layer.editingStopped.disconnect(self.toggle)
            except TypeError:  # missing connection
                pass
            layer.editingStopped.connect(self.toggle)
            try:
                layer.editingStarted.disconnect(self.toggle)
            except TypeError:  # missing connection
                pass
        else:
            self.freehand_edit.setEnabled(False)
            self.spinBoxAction.setEnabled(False)
            if (layer.type() == QgsMapLayer.VectorLayer and
                    (layer.geometryType() == QGis.Line or
                     layer.geometryType() == QGis.Polygon)):
                try:  # remove any existing connection first
                    layer.editingStarted.disconnect(self.toggle)
                except TypeError:  # missing connection
                    pass
                layer.editingStarted.connect(self.toggle)
                try:
                    layer.editingStopped.disconnect(self.toggle)
                except TypeError:  # missing connection
                    pass

       
    
    def trim (self):
        # 4 - ATIVAR A FERRAMENTA DE SELEÇÃO "PERSONALIZADA"

        self.iface.activeLayer().setSelectedFeatures([])
        self.seletor = SelectionTool(self.iface,QgsWKBTypes.LineGeometry)
        self.canvas.setMapTool(self.seletor)
        self.seletor.twoSelected.connect(self.doWork)

    def doWork(self):
        print u'Deu certo!'
        # 5 - PEGAR AS DUAS GEOMETRIAS SELECIONADAS E VERIFICAR SE EXISTE INTERSEÇÃO
        for s in selecionadas.getFeatures():
            if s[0].geometry().intersection(s[1].geometry()):
                selecionadas.select(s[0].id()) 
        # 6 - PEGA O PONTO DE INTERSEÇÃO E VERIFICA QUAl É O ULTIMO VERTICE DA PRIMEIRA GEOMETRIA SELECIONADA
            
            feat = layer.getFeatures()

            for feature in feat:
                vertices = feature.geometry().asPolyline()
                points = []

                for v in vertices:
                    points.append(v)
    
        


    def selecaoMudou(self, added, removed, cleared):
        if len(added) > 2:
            selecionados = []
            for i in range(len(added)-3, len(added)):
                selecionados.append(added[i])
            
            self.iface.activeLayer().setSelectedFeatures(selecionados)
          