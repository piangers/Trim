# -*- coding: UTF-8 -*-
from qgis.core import QgsWKBTypes,QgsGeometry,QgsFeatureRequest,QgsFeature
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from selectiontool import SelectionTool
import resources_rc
import math
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
        self.seletor.twoSelected.connect(self.executeTrim) # cria a conecção ao receber o segundo click

    def expand (self):
        layer = self.iface.activeLayer() # pega a layer ativa
        if layer == None:
            QMessageBox.information (self.iface.mainWindow() ,  u'ATENÇÃO!' ,  u"Selecione uma camada antes de ativar a ferramenta!")
            return
        
        layer.setSelectedFeatures([]) # seta features como vazio
        self.seletor = SelectionTool(self.iface,QgsWKBTypes.LineGeometry) # cria um seletor e quando captura o segundo click, ele realiza a connecção.
        self.canvas.setMapTool(self.seletor)
        self.seletor.twoSelected.connect(self.executeExpand)

    def executeExpand(self, selecionadas):
        distancia = self.tolerancia

        layer = self.iface.activeLayer() # pega a layer ativa

        idParaAlongar = selecionadas[0]
        idDeTeste = selecionadas[1]

        featParaAlongar = layer.getFeatures(QgsFeatureRequest(idParaAlongar)).next()
        featDeTeste = layer.getFeatures(QgsFeatureRequest(idDeTeste)).next()

        geomParaAlongar = featParaAlongar.geometry()
        geomDeTeste = featDeTeste.geometry()

        if not geomParaAlongar.intersects(geomDeTeste):
            ultimoVertice = len(geomParaAlongar.asPolyline())-1
            extremidade1 = geomParaAlongar.vertexAt(0)
            extremidade2 = geomParaAlongar.vertexAt(ultimoVertice)
            extremidade = -1
            distancia1 = extremidade1.distance(geomDeTeste.nearestPoint(QgsGeometry.fromPoint(extremidade1)).asPoint())
            distancia2 = extremidade2.distance(geomDeTeste.nearestPoint(QgsGeometry.fromPoint(extremidade2)).asPoint())
            if distancia1 < distancia2:
                extremidade = 0
            else:
                extremidade = ultimoVertice
    
            adj1, adj2 = geomParaAlongar.adjacentVertices(extremidade)
            adj = adj1 if (adj1 != -1) else adj2

            ultimo = geomParaAlongar.vertexAt(extremidade)
            anterior = geomParaAlongar.vertexAt(adj)

            angulo = math.atan((ultimo.y() - anterior.y())/(ultimo.x() - anterior.x()))

            novoX = ultimo.x() + distancia * math.cos(angulo)
            novoY = ultimo.y() + distancia * math.sin(angulo)

            layer.startEditing()
            layer.moveVertex(novoX, novoY, idParaAlongar, extremidade)
            layer.commitChanges()

            featParaAlongar = layer.getFeatures(QgsFeatureRequest(selecionadas[0])).next()
            novaGeom = featParaAlongar.geometry()
            if not novaGeom.intersects(geomDeTeste):
                QMessageBox.information (self.iface.mainWindow() ,  u'ATENÇÃO!' ,  u"As linhas selecionadas excedem a tolerância definida!")
                layer.startEditing()
                layer.moveVertex(ultimo.x(), ultimo.y(), idParaAlongar, extremidade)
                layer.commitChanges()
            
            else:
                selecionadas2 = [featParaAlongar.id(),featDeTeste.id()]
                self.executeTrim(selecionadas2)
        else:
            QMessageBox.information (self.iface.mainWindow() ,  u'ATENÇÃO!' ,  u"As feições selecionadas já possuem interseção! Escolha outra feição ou utilize a ferramenta Trim.")
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
            QMessageBox.information (self.iface.mainWindow() ,  u'ATENÇÃO!' ,  u"Não há interseção entre as feições selecionadas! Escolha outra feição ou utiliza a ferramneta Expand")
        else:
            sucesso, splits, topo = geom0.splitGeometry(geom1.asPolyline(), True)
            geomNova1 = splits[0]
            geomAntiga = geom0
            geomNova2 = geomAntiga.difference(geomNova1) # diference é a segunda parte do split da feição criada nos moldes da original e dividida. 
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