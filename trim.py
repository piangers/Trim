# -*- coding: UTF-8 -*-
from qgis.core import *
from qgis.gui import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import math
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
        self.expandAction = QAction(QIcon(":/plugins/Trim/ex.png"), u'Expand', self.iface.mainWindow())
        self.spinBox = QDoubleSpinBox(self.iface.mainWindow())
        self.toolbar = self.iface.addToolBar(u'Trim tools')
        # 2 - CONECTAR O CLIQUE DO BOTÃO COM UM MÉTODO ("SLOT")
        self.trimAction.triggered.connect(self.trim)
        self.expandAction.triggered.connect(self.expand)
        self.spinBox.valueChanged.connect(self.setTolerancia)
       
        #Padrões fixados
        
        self.spinBox.setDecimals(1)
        self.spinBox.setMinimum(0.000)
        self.spinBox.setMaximum(5000.000)
        self.spinBox.setSingleStep(0.100)
        self.tolerancia = self.spinBox.value()
        self.spinBox.setToolTip("Tolerancia")
        #self.spinBoxAction.setEnabled(False)

        self.toolbar.addAction(self.trimAction)
        self.toolbar.addAction(self.expandAction)
        self.toolbar.addWidget(self.spinBox)
 
    def unload(self):
        del self.toolbar
        
        try:
            self.canvas.unsetMapTool(self.seletor)
        except:
            pass

    def setTolerancia(self, t):
        self.tolerancia = t

    def trim (self,auto):
        # 4 - ATIVAR A FERRAMENTA DE SELEÇÃO "PERSONALIZADA"
        
        layer = self.iface.activeLayer() # pega a layer ativa
        if layer == None:
            print u'Selecione uma camada antes de ativar a ferramenta!'
            return
        
        layer.setSelectedFeatures([])
        self.seletor = SelectionTool(self.iface,QgsWKBTypes.LineGeometry)
        self.canvas.setMapTool(self.seletor)
        self.seletor.twoSelected.connect(self.doWork)

    def expand (self):
        layer = self.iface.activeLayer() # pega a layer ativa
        if layer == None:
            print u'Selecione uma camada antes de ativar a ferramenta!'
            return
        
        layer.setSelectedFeatures([])
        self.seletor = SelectionTool(self.iface,QgsWKBTypes.LineGeometry)
        self.canvas.setMapTool(self.seletor)
        self.seletor.twoSelected.connect(self.doWork2)

    def doWork2(self, selecionadas):
        dist = self.tolerancia

        layer = self.iface.activeLayer()

        idParaAlongar = selecionadas[0]
        idDeTeste = selecionadas[1]

        featParaAlongar = layer.getFeatures(QgsFeatureRequest(idParaAlongar)).next()
        featDeTeste = layer.getFeatures(QgsFeatureRequest(idDeTeste)).next()

        geomParaAlongar = featParaAlongar.geometry()
        geomDeTeste = featDeTeste.geometry()

        if not geomParaAlongar.intersects(geomDeTeste):
            ultimoVertice = len(geomParaAlongar.asPolyline())-1
            extr1 = geomParaAlongar.vertexAt(0)
            extr2 = geomParaAlongar.vertexAt(ultimoVertice)

            extr = -1
            dist1 = extr1.distance(geomDeTeste.nearestPoint(QgsGeometry.fromPoint(extr1)).asPoint())
            dist2 = extr2.distance(geomDeTeste.nearestPoint(QgsGeometry.fromPoint(extr2)).asPoint())
            if dist1 < dist2:
                extr = 0
            else:
                extr = ultimoVertice
    
            adj1, adj2 = geomParaAlongar.adjacentVertices(extr)
            adj = adj1 if (adj1 != -1) else adj2

            ultimo = geomParaAlongar.vertexAt(extr)
            anterior = geomParaAlongar.vertexAt(adj)

            ang = math.atan((ultimo.y() - anterior.y())/(ultimo.x() - anterior.x()))

            novoX = ultimo.x() + dist * math.cos(ang)
            novoY = ultimo.y() + dist * math.sin(ang)

            layer.startEditing()
            layer.moveVertex(novoX, novoY, idParaAlongar, extr)
            layer.commitChanges()

            featParaAlongar = layer.getFeatures(QgsFeatureRequest(selecionadas[0])).next()
            novaGeom = featParaAlongar.geometry()
            if not novaGeom.intersects(geomDeTeste):
                layer.startEditing()
                layer.moveVertex(ultimo.x(), ultimo.y(), idParaAlongar, extr)
                layer.commitChanges()
            
            else:
                selecionadas2 = [featParaAlongar.id(),featDeTeste.id()]
                self.doWork(selecionadas2)

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
            print ('Não há intersecção entre as feições selecionadas!')
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