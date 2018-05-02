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
        self.trimAction = QAction(QIcon(":/plugins/Trim/tr.png"), u'Trim', self.iface.mainWindow())
        self.toolbar = self.iface.addToolBar(u'Trim tools')
        self.toolbar.addAction(self.trimAction)

        # 2 - CONECTAR O CLIQUE DO BOTÃO COM UM MÉTODO ("SLOT")
        self.trimAction.triggered.connect(self.trim)

        # 3 - MÉTODO TRIM

    def unload(self):
        del self.toolbar
        self.canvas.unsetMapTool(self.seletor)

    '''
        settings = QSettings()
        # Create action
        self.freehand_edit = \
            QAction(QIcon(":/plugins/freehandEditing/l.png"),
                    "Freehand editing", self.iface.mainWindow())
        self.freehand_edit.setEnabled(False)
        self.freehand_edit.setCheckable(True)
        # Add toolbar button and menu item
        self.iface.digitizeToolBar().addAction(self.freehand_edit)
        self.iface.editMenu().addAction(self.freehand_edit)

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

        # Connect to signals for button behaviour
        self.freehand_edit.activated.connect(self.freehandediting)
        self.iface.currentLayerChanged['QgsMapLayer*'].connect(self.toggle)
        self.canvas.mapToolSet['QgsMapTool*'].connect(self.deactivate)
        self.spinBox.valueChanged[float].connect(self.tolerancesettings)

        # Get the tool
        self.tool = Trim(self.canvas)

    def tolerancesettings(self):
        settings = QSettings()
        settings.setValue("/freehandEdit/tolerance", self.spinBox.value())

    def freehandediting(self):
        self.canvas.setMapTool(self.tool)
        self.freehand_edit.setChecked(True)
        self.tool.rbFinished['QgsGeometry*'].connect(self.createFeature)
        self.active = True
    '''    
    
    def trim (self):
        # 4 - ATIVAR A FERRAMENTA DE SELEÇÃO "PERSONALIZADA"

        self.iface.activeLayer().setSelectedFeatures([])
        self.seletor = SelectionTool(self.iface,QgsWKBTypes.LineGeometry)
        self.canvas.setMapTool(self.seletor)
        self.seletor.twoSelected.connect(self.doWork)

    def doWork(self):
        print u'Deu certo!'

'''
        intersections = []
        mc = self.canvas
        layer1 = mc.currentLayer()
        layer2 = 
        if layer is None:
            return
        if layer.geometryType() == QGis.Line:
        elif geometry.intersection(0)
        

        # exemplo de interseção
        
        for a in layer1.getFeatures():
            for b in layer2.getFeatures():
                if a.geometry.intersects(b.geometry()):
                    intersection = a.geometry().intersection(b.geometry())
                    intersections.append(intersection.geometry().area())

    def selecaoMudou(self, added, removed, cleared):
        if len(added) > 2:
            selecionados = []
            for i in range(len(added)-3, len(added)):
                selecionados.append(added[i])
            
            self.iface.activeLayer().setSelectedFeatures(selecionados)

 '''           