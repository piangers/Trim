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

    def trim (self):
        
        layer = self.iface.activeLayer() # pega a layer ativa
        if layer == None:
            QMessageBox.information (self.iface.mainWindow() ,  u'ATENÇÃO!' ,  u"Selecione uma camada antes de ativar a ferramenta!")
            return
        
        layer.setSelectedFeatures([]) # seta features como vazio
        self.seletor = SelectionTool(self.iface,QgsWKBTypes.LineGeometry)
        self.canvas.setMapTool(self.seletor)
        self.seletor.twoSelected.connect(self.executeTrim)

    def expand (self):
        layer = self.iface.activeLayer() # pega a layer ativa
        if layer == None:
            QMessageBox.information (self.iface.mainWindow() ,  u'ATENÇÃO!' ,  u"Selecione uma camada antes de ativar a ferramenta!")
            return
        
        layer.setSelectedFeatures([]) # seta features como vazio
        self.seletor = SelectionTool(self.iface,QgsWKBTypes.LineGeometry)
        self.canvas.setMapTool(self.seletor)
        self.seletor.twoSelected.connect(self.executeExpand)

    def executeExpand(self, selecionadas):
        dist = self.tolerancia

        layer = self.iface.activeLayer() # pega a layer ativa

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
                QMessageBox.information (self.iface.mainWindow() ,  u'ATENÇÃO!' ,  u"As linhas selecionadas excedem a tolerância definida!")
                layer.startEditing()
                layer.moveVertex(ultimo.x(), ultimo.y(), idParaAlongar, extr)
                layer.commitChanges()
            
            else:
                selecionadas2 = [featParaAlongar.id(),featDeTeste.id()]
                self.executeTrim(selecionadas2)
        
        self.expand()

    def executeTrim(self, selecionadas):
        layer = self.iface.activeLayer() # pegar a layer ativa
        # "selecionadas" recebe a lista com as features das feições selecionadas(2)
        
        # pegar as duas linhas    
        featureParaCortar = layer.getFeatures(QgsFeatureRequest(selecionadas[0])).next() # a linha a ser dividida
        featureDeCorte = layer.getFeatures(QgsFeatureRequest(selecionadas[1])).next() # a linha que faz a intersecão e serve de ponto para a divisão
        
        geom0 = featureParaCortar.geometry() # pega a geometria 
        geom1 = featureDeCorte.geometry() # pega a geometria

        if not geom0.intersects(geom1): # Se não existe interseção então mostra a mensagem
            QMessageBox.information (self.iface.mainWindow() ,  u'ATENÇÃO!' ,  u"Não há intersecção entre as feições selecionadas!")
        else:
            sucesso, splits, topo = geom0.splitGeometry(geom1.asPolyline(), True)
            geomNova1 = splits[0]
            geomAntiga = geom0
            geomNova2 = geomAntiga.difference(geomNova1)
            layer.startEditing()
            feat1 = QgsFeature()
            feat2 = QgsFeature()
            atributos = featureParaCortar.attributes()
            feat1.setAttributes(atributos)
            feat2.setAttributes(atributos)
            feat1.setGeometry(geomNova1)
            feat2.setGeometry(geomNova2)

            if(geomNova1.length() > self.tolerancia and geomNova2.length() > self.tolerancia):
                QMessageBox.information (self.iface.mainWindow() ,  u'ATENÇÃO!' ,  u"As linhas selecionadas excedem a tolerância definida!")
                layer.commitChanges()
                self.trim()
            else:
                layer.deleteFeature(featureParaCortar.id())

                if(geomNova1.length() > self.tolerancia):
                    layer.addFeature(feat1, True)

                if(geomNova2.length() > self.tolerancia):
                    layer.addFeature(feat2, True)

                layer.commitChanges()

        self.trim()