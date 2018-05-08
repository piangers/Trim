# -*- coding: UTF-8 -*-
from qgis.core import *
from qgis.gui import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from selectiontool import SelectionTool
import resources_rc
#Import own classes and tools


class Trim:

    def __init__(self, iface):
      # Save reference to the QGIS interface
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        self.active = False

    def initGui(self):
        # 1 - CRIAR UM BOTÃO PARA ATIVAR A FERRAMENTA
        settings = QSettings()
        self.freehand_edit = \
        self.trimAction = QAction(QIcon(":/plugins/Trim/tr.png"), u'Trim', self.iface.mainWindow())
        self.spinBox = QDoubleSpinBox(self.iface.mainWindow())
        #self.toolbar = self.iface.addToolBar(u'Trim tools')
        #self.freehand_edit.setEnabled(False)
        #self.freehand_edit.setCheckable(True)
        # Add toolbar button and menu item
        self.iface.digitizeToolBar().addAction(self.freehand_edit)
        self.iface.editMenu().addAction(self.freehand_edit)
        # 2 - CONECTAR O CLIQUE DO BOTÃO COM UM MÉTODO ("SLOT")
        self.trimAction.triggered.connect(self.trim)
       
        #Padrões fixados
        
        self.spinBox.setDecimals(3)
        self.spinBox.setMinimum(0.000)
        self.spinBox.setMaximum(5.000)
        self.spinBox.setSingleStep(0.100)
        self.spinBoxAction = \
        self.iface.digitizeToolBar().addWidget(self.spinBox)
        self.spinBox.setToolTip(" Tolerancia de Trim .")
        self.spinBoxAction.setEnabled(False)
        #self.toolbar.addAction(self.trimAction)
 
    def unload(self):
        self.iface.digitizeToolBar().removeAction(self.freehand_edit)
        self.iface.digitizeToolBar().removeAction(self.spinBoxAction)
        
        try:
            self.canvas.unsetMapTool(self.seletor)
        except:
            pass


    def trim (self):
        # 4 - ATIVAR A FERRAMENTA DE SELEÇÃO "PERSONALIZADA"

        self.iface.activeLayer().setSelectedFeatures([])
        self.seletor = SelectionTool(self.iface,QgsWKBTypes.LineGeometry)
        self.canvas.setMapTool(self.seletor)
        self.seletor.twoSelected.connect(self.doWork)

    def doWork(self, selecionadas):
        # "selecionadas" EH A LISTA COM AS FEATUREID DAS FEIÇÕES SELECIONADAS (2)
        print (u'Deu certo!')
        # PEGAR O COMPRIMENTO DAS DUAS LINHAS
        layer = self.iface.activeLayer()
        featureParaCortar = layer.getFeature(selecionadas[0])
        featureDeCorte = layer.getFeature(selecionadas[1])
        layer = iface.activeLayer()
        selected = []

        for feat in layer.getFeatures():
            selected.append(feat)

        feat0 = selected[0]
        feat1 = selected[1]
        geom0 = feat0.geometry()
        geom1 = feat1.geometry()

        sucesso, splits, topo = geom0.splitGeometry(geom1.asPolyline(), True)

        geomNova = splits[0]
        featNova = QgsFeature()

        atributosNovos = []

        for a in feat0.attributes():
            atributosNovos.append(None)

        featNova.setGeometry(geomNova)
        featNova.setAttributes(atributosNovos)
        layer.startEditing()
        layer.addFeature(featNova, True)
        layer.commitChanges()

        for feat in layer.getFeatures():
            geom = feat.geometry()
            if geom.equals(geomNova):
                    break

        idParaRemover = feat.id()
        print idParaRemover
        layer.startEditing()
        layer.deleteFeature(idParaRemover)
        layer.commitChanges()


    def selecaoMudou(self, added, removed, cleared):
        if len(added) > 2:
            selecionados = []
            for i in range(len(added)-3, len(added)):
                selecionados.append(added[i])
            
            self.iface.activeLayer().setSelectedFeatures(selecionados)





### SCRIPT PRA RODAR NO QGIS



layer = iface.activeLayer()
selected = []

for feat in layer.getFeatures():
    selected.append(feat)

feat0 = selected[0]
feat1 = selected[1]
geom0 = feat0.geometry()
geom1 = feat1.geometry()

sucesso, splits, topo = geom0.splitGeometry(geom1.asPolyline(), True)

geomNova = splits[0]
featNova = QgsFeature()

atributosNovos = []

for a in feat0.attributes():
    atributosNovos.append(None)

featNova.setGeometry(geomNova)
featNova.setAttributes(atributosNovos)
layer.startEditing()
layer.addFeature(featNova, True)
layer.commitChanges()

for feat in layer.getFeatures():
    geom = feat.geometry()
    if geom.equals(geomNova):
        break

idParaRemover = feat.id()
print idParaRemover
layer.startEditing()
layer.deleteFeature(idParaRemover)