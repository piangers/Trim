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
        self.trimAction = QAction(QIcon(":/plugins/Trim/tr.png"), u'Trim', self.iface.mainWindow())
        self.spinBox = QDoubleSpinBox(self.iface.mainWindow())
        self.toolbar = self.iface.addToolBar(u'Trim tools')
        # 2 - CONECTAR O CLIQUE DO BOTÃO COM UM MÉTODO ("SLOT")
        self.trimAction.triggered.connect(self.trim)
       
        #Padrões fixados
        
        self.spinBox.setDecimals(3)
        self.spinBox.setMinimum(0.000)
        self.spinBox.setMaximum(5.000)
        self.spinBox.setSingleStep(0.100)
        self.spinBox.setToolTip(" Tolerancia de Trim .")
        #self.spinBoxAction.setEnabled(False)

        self.toolbar.addAction(self.trimAction)
        self.toolbar.addWidget(self.spinBox)
 
    def unload(self):
        del self.toolbar
        
        try:
            self.canvas.unsetMapTool(self.seletor)
        except:
            pass


    def trim (self):
        # 4 - ATIVAR A FERRAMENTA DE SELEÇÃO "PERSONALIZADA"
        
        layer = self.iface.activeLayer() # pega a layer ativa
        if layer == None:
            print u'Selecione uma camada antes de ativar a ferramenta!'
            return
        
        layer.setSelectedFeatures([])
        self.seletor = SelectionTool(self.iface,QgsWKBTypes.LineGeometry)
        self.canvas.setMapTool(self.seletor)
        self.seletor.twoSelected.connect(self.doWork)

    def doWork(self, selecionadas):
        layer = self.iface.activeLayer() # pega a layer ativa
        # "selecionadas" EH A LISTA COM AS FEATUREID DAS FEIÇÕES SELECIONADAS (2)
        # PEGAR O COMPRIMENTO DAS DUAS LINHAS
            
        featureParaCortar = layer.getFeatures(QgsFeatureRequest(selecionadas[0])).next() # a linha a ser dividida
        featureDeCorte = layer.getFeatures(QgsFeatureRequest(selecionadas[1])).next() # a linha que faz a intersecão e serve de ponto para a divisão
        
        geom0 = featureParaCortar.geometry() # pega a geometria 
        geom1 = featureDeCorte.geometry() # pega a geometria

        sucesso, splits, topo = geom0.splitGeometry(geom1.asPolyline(), True)

        if len(splits) == 0:
            print u'Não há intersecção entre as feições selecionadas!'
            return

        geomNova1 = splits[0]
        geomAntiga = geom0
        geomNova2 = geomAntiga.difference(geomNova1)

        # geomMantidas = []
        # if geomNova1.length() > tolerancia:
        #     geomMantidas.append(geomNova1)

        # if geomNova2.length() > tolerancia:
        #     geomMantidas.append(geomNova2)
    
        # if len(geomMantidas) == 2:
        #     return
        # 
        # geomParaManter = geomMantidas[0]
        
        geomParaManter = QgsGeometry()
        if geomNova1.length() > geomNova2.length():
            geomParaManter = geomNova1
        else:
            geomParaManter = geomNova2
            
        featNova = QgsFeature()
        featAntiga = featureParaCortar

        atributos = featureParaCortar.attributes()

        featNova.setGeometry(geomParaManter)
        featNova.setAttributes(atributos)

        layer.startEditing()
        layer.addFeature(featNova, True)
        layer.deleteFeature(featAntiga.id())
        layer.commitChanges()


    def selecaoMudou(self, added, removed, cleared):
        if len(added) > 2:
            selecionados = []
            for i in range(len(added)-3, len(added)):
                selecionados.append(added[i])
            
            self.iface.activeLayer().setSelectedFeatures(selecionados)