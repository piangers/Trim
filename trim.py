# -*- coding: UTF-8 -*-
from qgis.core import QgsWKBTypes,QgsGeometry,QgsFeatureRequest,QgsFeature, QGis
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from selectiontool import SelectionTool
import resources_rc
import math


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
        self.trimAction.setCheckable(True)
        self.expandAction.setCheckable(True)

        self.spinBox = QDoubleSpinBox(self.iface.mainWindow())
        self.toolbar = self.iface.addToolBar(u'Trim tools')
        
        # 2 - CONECTAR O CLIQUE DO BOTÃO COM UM MÉTODO ("SLOT")
        self.trimAction.toggled.connect(self.trim)
        self.expandAction.toggled.connect(self.expand)
        self.spinBox.valueChanged.connect(self.setTolerancia)
       
        #Padrões fixados
        
        self.spinBox.setDecimals(1)
        self.spinBox.setMinimum(0.000)
        self.spinBox.setMaximum(5000.000)
        self.spinBox.setSingleStep(0.100)
        self.tolerancia = self.spinBox.value()
        self.spinBox.setToolTip("Tolerancia")
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
        self.tolerancia = t # recebendo tolerância atravéz de t.

    def trim (self, bip):
        
        layer = self.iface.activeLayer() # pega a layer ativa
        if layer == None:
            QMessageBox.information (self.iface.mainWindow() ,  u'ATENÇÃO!' ,  u"Selecione uma camada antes de ativar a ferramenta!")
            return
        if not layer.isEditable():
            QMessageBox.information (self.iface.mainWindow() ,  u'ATENÇÃO!' ,  u'É necessário ativar o modo de edição "Alterna edição", para utilizar a ferramenta!')
            return
        if layer.geometryType() != QGis.Line:
            QMessageBox.information (self.iface.mainWindow() ,  u'ATENÇÃO!' ,  u'A ferramenta só pode ser executada em camadas do tipo linha!')
            return

        if bip:
            if self.expandAction.isChecked():
                self.expandAction.setChecked(False)
            layer.setSelectedFeatures([]) # seta features como vazio
            self.seletor = SelectionTool(self.iface,QgsWKBTypes.LineGeometry)
            self.canvas.setMapTool(self.seletor)
            self.seletor.twoSelected.connect(self.executeTrim) # cria a conecção ao receber o segundo click
        else:
            self.canvas.unsetMapTool(self.seletor)

    def expand (self, bip):
        layer = self.iface.activeLayer() # pega a layer ativa
        if layer == None:
            QMessageBox.information (self.iface.mainWindow() ,  u'ATENÇÃO!' ,  u"Selecione uma camada antes de ativar a ferramenta!")
            return
        if not layer.isEditable():
            QMessageBox.information (self.iface.mainWindow() ,  u'ATENÇÃO!' ,  u'É necessário ativar o modo de edição "Alterna edição", para utilizar a ferramenta!')
            return

        if bip:
            if self.trimAction.isChecked():
                self.trimAction.setChecked(False)
            layer.setSelectedFeatures([]) # seta features como vazio
            self.seletor = SelectionTool(self.iface,QgsWKBTypes.LineGeometry) # cria um seletor e quando captura o segundo click, ele realiza a connecção.
            self.canvas.setMapTool(self.seletor)
            self.seletor.twoSelected.connect(self.executeExpand) # ao selecionar a segunda feature ele realiza a ação
        else:
            self.canvas.unsetMapTool(self.seletor)

    def executeExpand(self, selecionadas):
        distancia = self.tolerancia # distancia recebe a tolerância
        layer = self.iface.activeLayer() # pega a layer ativa
        idParaAlongar = selecionadas[0] # pega o id da primeira feature setada e no array de selecionadas
        idDeTeste = selecionadas[1] # pega o id da segunda feature setada e no array de selecionadas

        featParaAlongar = layer.getFeatures(QgsFeatureRequest(idParaAlongar)).next() # pega a primeira feature  selecionadas
        featDeTeste = layer.getFeatures(QgsFeatureRequest(idDeTeste)).next() # pega a segunda feature  selecionadas

        geomParaAlongar = featParaAlongar.geometry() # pega a geometria da primeira feature
        geomDeTeste = featDeTeste.geometry() # pega a geometria da segunda feature

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
            
            # Formula geometricas pra buscar o angulo
            angulo = math.atan((ultimo.y() - anterior.y())/(ultimo.x() - anterior.x()))
            novoX = ultimo.x() + distancia * math.cos(angulo) 
            novoY = ultimo.y() + distancia * math.sin(angulo)

            layer.moveVertex(novoX, novoY, idParaAlongar, extremidade)
            layer.commitChanges()
            layer.startEditing()
            featParaAlongar = layer.getFeatures(QgsFeatureRequest(selecionadas[0])).next()
            novaGeom = featParaAlongar.geometry()
            
            if not novaGeom.intersects(geomDeTeste):
                layer.moveVertex(ultimo.x(), ultimo.y(), idParaAlongar, extremidade)
                layer.commitChanges()
                layer.startEditing()
                QMessageBox.information (self.iface.mainWindow() ,  u'ATENÇÃO!' ,  u"As linhas selecionadas excedem a tolerância definida ou não respeitam as condições necessárias para a execução!")  
            else:
                selecionadas2 = [featParaAlongar.id(),featDeTeste.id()]
                self.executeTrim(selecionadas2)
        self.expand(True)
    
    def executeTrim(self, selecionadas):
        layer = self.iface.activeLayer() # pegar a layer ativa
        # "selecionadas" recebe a lista com as features das feições selecionadas(2)    
        featureParaCortar = layer.getFeatures(QgsFeatureRequest(selecionadas[0])).next() # a linha a ser dividida
        featureDeCorte = layer.getFeatures(QgsFeatureRequest(selecionadas[1])).next() # a linha que faz a intersecão e serve de ponto para a divisão
        geom0 = featureParaCortar.geometry() # pega a geometria 
        geom1 = featureDeCorte.geometry() # pega a geometria

        if not geom0.intersects(geom1): # Se não existe interseção então mostra a mensagem
            QMessageBox.information (self.iface.mainWindow() ,  u'ATENÇÃO!' ,  u"Não há interseção entre as feições selecionadas! Escolha outra feição.")
        else:
            sucesso, splits, topo = geom0.splitGeometry(geom1.asPolyline(), True)
            geomNova1 = splits[0]
            geomAntiga = geom0
            geomNova2 = geomAntiga.difference(geomNova1) # Segunda parte do split da feição criada nos moldes da original, só recebida se utilizar o "difference".
            feat1 = QgsFeature()
            feat2 = QgsFeature()
            atributos = featureParaCortar.attributes()
            feat1.setAttributes(atributos)
            feat2.setAttributes(atributos)
            feat1.setGeometry(geomNova1)
            feat2.setGeometry(geomNova2)
            
            if(geomNova1.length() > self.tolerancia and geomNova2.length() > self.tolerancia):
                QMessageBox.information (self.iface.mainWindow() ,  u'ATENÇÃO!' ,  u"As linhas selecionadas excedem a tolerância definida ou não respeitam as condições necessárias para a execução!")
                layer.commitChanges()
                layer.startEditing()
                self.trim(True)   
            else:
                layer.deleteFeature(featureParaCortar.id())
                if(geomNova1.length() > self.tolerancia):
                    layer.addFeature(feat1, True)
                
                if(geomNova2.length() > self.tolerancia):
                    layer.addFeature(feat2, True)
                
                layer.commitChanges()
                layer.startEditing()
        self.trim(True)
