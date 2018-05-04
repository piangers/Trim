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

    def doWork(self):
        print u'Deu certo!'
        # 5 - PEGAR AS DUAS GEOMETRIAS SELECIONADAS E VERIFICAR SE EXISTE INTERSEÇÃO
        # for s in self.iface.selecionadas.getFeatures():
        #     if s[0].geometry().intersection(s[1].geometry()):
        #         self.iface.selecionadas.select(s[0].id()) 
        # # 6 - PEGA O PONTO DE INTERSEÇÃO E VERIFICA QUAl É O ULTIMO VERTICE DA PRIMEIRA GEOMETRIA SELECIONADA
            
        #     # feat = self.iface.selecionadas.getFeatures()

        #     # for feature in feat:
        #     #     vertices = feature.geometry().asPolyline()
        #     #     points = []

        #     #     for v in vertices:
        #     #         points.append(v)
    
        


    def selecaoMudou(self, added, removed, cleared):
        if len(added) > 2:
            selecionados = []
            for i in range(len(added)-3, len(added)):
                selecionados.append(added[i])
            
            self.iface.activeLayer().setSelectedFeatures(selecionados)

def deactivate(self):
        self.freehand_edit.setChecked(False)
        if self.active:
            self.tool.rbFinished['QgsGeometry*'].disconnect(self.createFeature)
        self.active = False