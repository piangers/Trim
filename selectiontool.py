# -*- coding: UTF-8 -*-
from qgis.core import QgsFeature
from qgis.gui import *
from PyQt4.QtCore import *

class SelectionTool(QgsMapToolIdentify):
    
    twoSelected = pyqtSignal([int])

    def __init__(self, iface, geomType):
        super(SelectionTool, self).__init__(iface.mapCanvas())
        self.setCursor(Qt.CrossCursor)
        self.geomType = geomType
        self.iface = iface
        self.selecionadas = []
        
    def canvasReleaseEvent(self, event):
        #PEGA TODAS AS FEATURES DO PONTO CLICADO
        found_features = self.identify(event.x(), event.y(), self.ActiveLayer, self.VectorLayer)
        final_features = []
        
        #SE FOREM ENCONTRADAS FEATURES NO PONTO CLICADO...
        if len(found_features) > 0:
            for feat in found_features:
                #SE A FEATURE FOR DO TIPO DE GEOMETRIA DA FERRAMENTA, COLOCAR NO final_features
                if feat.mLayer.geometryType() == self.geomType:
                    final_features.append(feat)
        
        #SE O TOTAL DE FEATURES PARA O TIPO DE GEOMETRIA DA FERRAMENTA FOR MAIOR QUE ZERO...
        if len(final_features) > 0:
            feature = final_features[0].mFeature
            layer = final_features[0].mLayer
            featureId = feature.id()
            
            #CHECAR SE A FEATURE JA NAO ESTAVA SELECIONADA ANTES. SE SIM, DESSELECIONAR.
            if feature.id() in layer.selectedFeaturesIds():
                layer.deselect(feature.id())
                self.selecionadas.remove(featureId)
            
            #SE NAO ESTAVA SELECIONADA ANTES...
            else:
                if len(self.selecionadas) != 2:
                    layer.select(feature.id())
                    self.selecionadas.append(featureId)
                    if len(self.selecionadas) == 2:
                        self.twoSelected.emit(self.selecionadas)
