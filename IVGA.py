# -*- coding: utf-8 -*-
from PyQt5 import QtNetwork
from PyQt5.QtCore import Qt, QCoreApplication, QDateTime, QCoreApplication, QUrl
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QDialog, QAction, QMessageBox, QFileDialog, QTableWidgetItem, QFrame, QComboBox, QCheckBox, QWidget, QHBoxLayout
from qgis.core import QgsProject, QgsWkbTypes, QgsMapLayer, QgsFeature, QgsGeometry, QgsPointXY
import string

import os
import sys

from .IVGA_dialog import Ui_IVGA_dialog


class IVGA(QDialog):

    def __init__(self, iface):
        self.z = ""

        super(IVGA, self).__init__()
        self.iface = iface

        if sys.platform.upper().startswith("WIN"):
            self.so = "W"
        else:
            self.so = "L"

        self.plugin_dir = self.manage_slash(os.path.dirname(__file__))
        self.project_dir = ""
        self.actions = ""
        self.menu = self.tr(u'&IVGA')
        self.toolbar = self.iface.addToolBar(u'IVGA')
        self.toolbar.setObjectName(u'IVGA')
        self.iface.newProjectCreated.connect(self.change_project)
        self.iface.projectRead.connect(self.change_project)
        self.layer = None
        self.elems = None


    def tr(self, message):
        return QCoreApplication.translate('IVGA', message)


    def manage_slash(self, bar):
        """ Manage slash '/', '\' """

        if bar.strip() == "" : return ""
        if self.so == "W":
            z = bar.replace('/', '\\')
            if str(z)[-1] == "\\" : z = z[0:-1]
        else :
            z = bar.replace('\\', '/')
            if str(z)[-1] == "/" : z = z[0:-1]

        return z


    def fill_zeros(self, v, n):
        """ Fill zeros """

        if len(str(v)) < n:
            return str("0000000000"[0:n-len(str(v))]) + str(v)
        else:
            return str(v)


    def initGui(self):

        # Config menu action
        icon = QIcon(self.manage_slash(self.plugin_dir + "/IVGA.png"))
        self.action = QAction(icon, "IVGA", self.iface.mainWindow())
        self.action.setObjectName("IVGA")
        self.action.setWhatsThis("Parcela Catastral GML")
        self.action.setStatusTip("Parcela Catastral GML")
        self.action.triggered.connect(self.run)

        # Config button
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("&IVGA", self.action)
        
        # Config form
        self.ui = Ui_IVGA_dialog()
        self.ui.setupUi(self)
        self.ui.Logo.setPixmap(QPixmap(self.manage_slash(self.plugin_dir + "/IVGA.png")))
        self.ui.Validar.clicked.connect(self.check_refs)
        self.ui.Carpeta.setIcon(QIcon(self.manage_slash(self.plugin_dir + "/folder.png")))
        self.ui.Carpeta.clicked.connect(self.select_folder)
        self.ui.Idioma.currentIndexChanged.connect(self.ui.retranslateUi)
        self.ui.Crear.clicked.connect(self.create_gml)
        self.ui.Cerrar.clicked.connect(self.close)


    def unload(self):

        # Remove icons and actions
        self.iface.removePluginMenu(self.tr(u'&IVGA'),self.action)
        self.iface.removeToolBarIcon(self.action)
        self.iface.newProjectCreated.disconnect(self.change_project)
        self.iface.projectRead.disconnect(self.change_project)
        self.ui.Validar.clicked.connect(self.check_refs)
        self.ui.Idioma.currentIndexChanged.connect(self.ui.retranslateUi)
        self.ui.Carpeta.clicked.disconnect(self.select_folder)
        self.ui.Crear.clicked.disconnect(self.create_gml)
        self.ui.Cerrar.clicked.disconnect(self.close)
        del self.toolbar

            
    def show_message(self, av, t):
        """ Show message to user """

        m = QMessageBox()
        m.setText(self.tr(t))
        if av == "P":
            m.setIcon(QMessageBox.Information)
            m.setWindowTitle("Pregunta")
            m.setStandardButtons(QMessageBox.Ok | QMessageBox.No)
            b1 = m.button(QMessageBox.Ok)
            b1.setText("Si")
            b2 = m.button(QMessageBox.No)
            b2.setText("No")
        else:
            if av == "W":
                m.setIcon(QMessageBox.Warning)
                z = "Atención"
            elif av == "C":
                m.setIcon(QMessageBox.Critical)
                z = "Error"
            else:
                m.setIcon(QMessageBox.Information)
            m.setWindowTitle("Aviso")
            m.setStandardButtons(QMessageBox.Ok)
            b = m.button(QMessageBox.Ok)
            b.setText("Seguir")

        return m.exec_()


    def change_project(self):
        """ Update project folder """

        self.project_dir = self.manage_slash(QgsProject.instance().homePath())


    def select_folder(self):
        """ Select destination folder """

        msg = "Selección carpeta destino"
        z = QFileDialog.getExistingDirectory(None, msg, self.ui.desti.text(), QFileDialog.ShowDirsOnly)
        if z.strip() != "":
            self.ui.desti.setText(self.manage_slash(z))


    def create_gml(self):
        """ Create GML file with Format INSPIRE """
        # Set INSPIRE version
        iv = 3
        if self.ui.Inspire4.isChecked():
            iv = 4

        self.z = self.header_gml(iv)
        if self.ui.check.isChecked():
            if self.check_refs():
                self.write_gml()
        else:
            self.write_gml()
        

    def write_gml(self):
        iv = 3
        if self.ui.Inspire4.isChecked():
            iv = 4

         # Check filename
        filename = str(self.ui.fileName.text())
        if filename == "":
            if self.show_message("W", self.ui.msg_noName) == QMessageBox.Ok:
                return
        else:
            f = self.manage_slash(self.ui.desti.text() + "/" + filename + ".gml")
            if os.path.exists(f):
                if self.show_message("P", self.ui.msg_fileExists.format(filename)) == QMessageBox.No:
                    return


        total = self.ui.Selec.rowCount()
        for fil in range(total):
            ref = self.ui.Selec.item(fil, 1).text()
                     
            area = self.ui.Selec.item(fil, 4).text()
            namespace = self.ui.Selec.cellWidget(fil, 5).currentText()
            localId = ""
            if ref != "" and len(ref) == 14 and namespace == 'SDGC':
                localId = ref
            else:
                localId = self.ui.Selec.item(fil, 3).text()


            # Get list of points of selected polygon
            polygon = self.geo[fil]
            rings = self.get_rings(polygon)
            
            if len(rings) == 0:
                return 

            bou = self.geo[fil].boundingBox()
            min = str(format(bou.xMinimum(),"f")) + " " + str(format(bou.yMinimum(), "f"))
            max = str(format(bou.xMaximum(),"f")) + " " + str(format(bou.yMaximum(), "f"))
            epsg = self.crs.split(":")[1]
            
            self.z += self.body_gml(iv, epsg, localId, area, namespace, rings, min, max)

        self.z += self.footer_gml(iv)

        # Generate GML file
        fg = open(f, "w+")
        fg.write(self.z)
        fg.close()
        
        self.show_message("M", self.ui.msg_done.format(filename))


    def header_gml(self, v):
        """ GML header """

        if v == 3:
            z='<?xml version="1.0" encoding="utf-8"?>\n'
            z+='<!-- Archivo generado automaticamente por el plugin Export GML catastro de España de QGIS. -->\n'
            z+='<!-- Parcela Catastral de la D.G. del Catastro. -->\n'
            z+='<gml:FeatureCollection gml:id="ES.SDGC.CP" xmlns:gml="http://www.opengis.net/gml/3.2" '
            z+='xmlns:gmd="http://www.isotc211.org/2005/gmd" '
            z+='xmlns:ogc="http://www.opengis.net/ogc" '
            z+='xmlns:xlink="http://www.w3.org/1999/xlink" '
            z+='xmlns:cp="urn:x-inspire:specification:gmlas:CadastralParcels:3.0" '
            z+='xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            z+='xsi:schemaLocation="urn:x-inspire:specification:gmlas:CadastralParcels:3.0 '
            z+='http://inspire.ec.europa.eu/schemas/cp/3.0/CadastralParcels.xsd">\n'
        else:
            z='<?xml version="1.0" encoding="utf-8"?>\n'
            z+='<!-- Archivo generado automaticamente por el plugin IVGA de QGIS. -->\n'
            z+='<!-- Parcela Catastral para entregar a la D.G. del Catastro. Formato INSPIRE v4. -->\n'
            z+='<FeatureCollection '
            z+='xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            z+='xmlns:gml="http://www.opengis.net/gml/3.2" '
            z+='xmlns:xlink="http://www.w3.org/1999/xlink" '
            z+='xmlns:cp="http://inspire.ec.europa.eu/schemas/cp/4.0" '
            z+='xmlns:gmd="http://www.isotc211.org/2005/gmd" '
            z+='xsi:schemaLocation="http://www.opengis.net/wfs/2.0 http://schemas.opengis.net/wfs/2.0/wfs.xsd http://inspire.ec.europa.eu/schemas/cp/4.0 http://inspire.ec.europa.eu/schemas/cp/4.0/CadastralParcels.xsd" '
            z+='xmlns="http://www.opengis.net/wfs/2.0" '
            z+='timeStamp="{}" '.format(self.ui.data.dateTime().toString(Qt.ISODate))
            z+='numberMatched="1" '
            z+='numberReturned="1">\n'

        return z


    def body_gml(self, v, epsg, localId, area, namespace, rings, min, max) :

        exterior_ring = rings[0]
        [punN, punL] = self.get_points(exterior_ring)
        if len(rings) > 1:
            interior_rings = rings[1]
        
        """ GML body """

        if v == 3:
            z='<gml:featureMember>\n<cp:CadastralParcel gml:id="ES.'+namespace+'.CP.'+str(localId)+'">\n<gml:boundedBy>\n'
            z+='<gml:Envelope srsName="urn:ogc:def:crs:EPSG::'+str(epsg)+'">\n'
            z+='<gml:lowerCorner>'+str(min)+'</gml:lowerCorner>\n<gml:upperCorner>'+str(max)+'</gml:upperCorner>\n'
            z+='</gml:Envelope>\n</gml:boundedBy>\n<cp:areaValue uom="m2">'+str(area)+'</cp:areaValue>\n'
            z+='<cp:beginLifespanVersion>'+self.ui.data.dateTime().toString(Qt.ISODate)+'</cp:beginLifespanVersion>\n'
            z+='<cp:endLifespanVersion xsi:nil="true" nilReason="other:unpopulated"></cp:endLifespanVersion>\n<cp:geometry>\n'
            z+='<gml:MultiSurface gml:id="MultiSurface_ES.'+namespace+'.CP.'+str(localId)+'" srsName="urn:ogc:def:crs:EPSG::'+str(epsg)+'">\n<gml:surfaceMember>\n'
            z+='<gml:Surface gml:id="Surface_ES.'+namespace+'.CP.'+str(localId)+'.1" srsName="urn:ogc:def:crs:EPSG::'+str(epsg)+'">\n'
            z+='<gml:patches>\n<gml:PolygonPatch>'

            z+='\n<gml:exterior>\n<gml:LinearRing>\n'
            z+='<gml:posList srsDimension="2" count="'+str(punN)+'">'+str(punL)+'</gml:posList>\n'
            z+='</gml:LinearRing>\n</gml:exterior>' 
            if len(interior_rings) > 0:
                for ring in interior_rings:
                    [punN, punL] = self.get_points(ring)
                    z+= '\n<gml:interior>\n<gml:LinearRing>\n'
                    z+='<gml:posList srsDimension="2" count="'+str(punN)+'">'+str(punL)+'</gml:posList>\n'
                    z+='</gml:LinearRing>\n</gml:interior>'
            
            z+= '\n</gml:PolygonPatch>\n</gml:patches>\n</gml:Surface>\n</gml:surfaceMember>\n</gml:MultiSurface>\n'
            z+='</cp:geometry>\n<cp:inspireId xmlns:base="urn:x-inspire:specification:gmlas:BaseTypes:3.2">\n<base:Identifier>\n'
            z+='<base:localId>'+str(localId)+'</base:localId>\n'
            z+='<base:namespace>ES.'+namespace+'.CP</base:namespace>\n</base:Identifier>\n</cp:inspireId>\n<cp:label>'+str(localId)+'</cp:label>\n'
            z+='<cp:nationalCadastralReference>2</cp:nationalCadastralReference>\n'
            z+='<cp:validFrom xsi:nil="true" nilReason="other:unpopulated"></cp:validFrom>\n<cp:validTo xsi:nil="true" nilReason="other:unpopulated"></cp:validTo>\n'
            z+='</cp:CadastralParcel>\n</gml:featureMember>\n'
            
        else:
            z='<member>\n' 
            z+='<cp:CadastralParcel gml:id="ES.'+namespace+'.CP.'+str(localId)+'">\n'
            z+='<cp:areaValue uom="m2">'+str(area)+'</cp:areaValue>\n'
            z+='<cp:beginLifespanVersion xsi:nil="true" nilReason="http://inspire.ec.europa.eu/codelist/VoidReasonValue/Unpopulated"></cp:beginLifespanVersion>\n'
            z+='<cp:endLifespanVersion xsi:nil="true" nilReason="http://inspire.ec.europa.eu/codelist/VoidReasonValue/Unpopulated"></cp:endLifespanVersion>\n'
            z+='<cp:geometry>\n'
            z+='<gml:MultiSurface gml:id="MultiSurface_ES.'+namespace+'.CP.'+str(localId)+'" srsName="http://www.opengis.net/def/crs/EPSG/0/'+str(epsg)+'">\n'
            z+='<gml:surfaceMember>\n'
            z+='<gml:Surface gml:id="Surface_ES.'+namespace+'.CP.'+str(localId)+'.1" srsName="http://www.opengis.net/def/crs/EPSG/0/'+str(epsg)+'">\n'
            z+='<gml:patches>\n<gml:PolygonPatch>'

            z+= '\n<gml:exterior>\n<gml:LinearRing>\n'
            z+='<gml:posList srsDimension="2">'+str(punL)+'</gml:posList>'
            z+='\n</gml:LinearRing>\n</gml:exterior>'
            if len(interior_rings) > 0:
                for ring in interior_rings:
                    [punN, punL] = self.get_points(ring)
                    z+= '\n<gml:interior>\n<gml:LinearRing>\n'
                    z+='<gml:posList srsDimension="2">'+str(punL)+'</gml:posList>\n'
                    z+='</gml:LinearRing>\n</gml:interior>'

            z+='\n</gml:PolygonPatch>\n</gml:patches>\n</gml:Surface>\n</gml:surfaceMember>\n</gml:MultiSurface>\n</cp:geometry>\n'
            z+='<cp:inspireId>\n<Identifier xmlns="http://inspire.ec.europa.eu/schemas/base/3.3">\n'
            z+='<localId>'+str(localId)+'</localId>\n<namespace>ES.'+namespace+'.CP</namespace>\n</Identifier>\n</cp:inspireId>\n'
            z+='<cp:label/>\n<cp:nationalCadastralReference/>'
            z+='\n</cp:CadastralParcel>\n'
            z+='</member>\n'

        return z


    def footer_gml(self,v) :
        """ GML footer """

        if v == 3:
            z = '</gml:FeatureCollection>\n'
        else:
            z = '</FeatureCollection>\n'

        return z
        

    def check_refs(self):
        self.finishedRequests = 0
        total = self.ui.Selec.rowCount()
        self.refsToCheck = []
        self.notFound = []
        bbox = self.layer.boundingBoxOfSelected()
        xmin, xmax, ymin, ymax = bbox.xMinimum(), bbox.yMinimum(), bbox.xMaximum(), bbox.yMaximum()
        bbox = '{},{},{},{}'.format(xmin, xmax, ymin, ymax)

        self.manager_NPO = QtNetwork.QNetworkAccessManager()
        self.manager_NPO.finished.connect(self.handleResponse_NPO)
        url = 'http://ovc.catastro.meh.es/INSPIRE/wfsCP.aspx?service=wfs&request=getfeature&Typenames=cp.cadastralparcel&SRSname=EPSG::{}&bbox={}'.format(str(self.crs.split(":")[1]), bbox)
        print('petición: {}'.format(url))
        
        req = QtNetwork.QNetworkRequest(QUrl(url))
        self.manager_NPO.get(req)

        self.NPP = total
        for fil in range(total):
            ref = self.ui.Selec.item(fil, 1).text().upper()
            if len(ref) == 14 :
                self.refsToCheck.append([ref,fil])
            else:
                self.ui.Selec.cellWidget(fil, 5).setCurrentIndex(0)

        self.manager = QtNetwork.QNetworkAccessManager()
        allChecked = self.manager.finished.connect(self.handleResponse)
        if len(self.refsToCheck) > 0:
            for item in self.refsToCheck:
                url = 'http://ovc.catastro.meh.es/INSPIRE/wfsCP.aspx?service=wfs&version=2&request=getfeature&STOREDQUERIE_ID=GetParcel&refcat={}&srsname=EPSG::{}'.format(item[0],str(self.crs.split(":")[1]))
                print('petición: {}'.format(url))
                req = QtNetwork.QNetworkRequest(QUrl(url))
                self.manager.get(req)
        else:
            allChecked = True            

        return allChecked

    def handleResponse(self, reply):
        er = reply.error()
        if er == QtNetwork.QNetworkReply.NetworkError.NoError:
            bytes_string = reply.readAll()
            response = str(bytes_string, 'utf-8')
            #print(response)
            if 'Exception' in response:
                start = response.index('<ExceptionText><![CDATA[No se ha encontrado la parcela ') + len('<ExceptionText><![CDATA[No se ha encontrado la parcela ')
                end = start + 14
                ref = response[start:end]
                for i in range(len(self.refsToCheck)):
                    if self.refsToCheck[i][0] == ref:    
                        fil = self.refsToCheck[i][1]
                        if self.ui.Selec.cellWidget(fil, 2).isChecked():
                            self.notFound.append(ref)
                            self.ui.Selec.cellWidget(fil, 2).setChecked(False)
                        self.ui.Selec.item(fil, 3).setText(string.ascii_uppercase[fil])
                        self.ui.Selec.cellWidget(fil, 5).setCurrentIndex(0)

            elif 'cp:CadastralParcel' in response:
                start = response.index('<localId>') + len('<localId>')
                end = start + 14
                ref = response[start:end]
                for i in range(len(self.refsToCheck)):
                    if self.refsToCheck[i][0] == ref:    
                        fil = self.refsToCheck[i][1]
                        if self.ui.Selec.cellWidget(fil, 2).isChecked():
                            self.ui.Selec.item(fil, 3).setText(ref)
                            self.ui.Selec.cellWidget(fil, 5).setCurrentIndex(1)
                        else:
                            self.ui.Selec.item(fil, 3).setText(string.ascii_uppercase[fil])
                            self.ui.Selec.cellWidget(fil, 5).setCurrentIndex(0)

            if fil == self.refsToCheck[-1][1]:
                if self.finishedRequests > 0: 
                    self.display_options()
                else:
                    self.finishedRequests +=1
                if len(self.notFound) > 0 :
                    msg = ''
                    for ref in self.notFound:
                        msg += '\n' + ref
                    self.show_message("W", self.ui.msg_notFound.format(msg))
                return True
        return False


    def handleResponse_NPO(self, reply):
        er = reply.error()
        self.wfsElems = []
        if er == QtNetwork.QNetworkReply.NetworkError.NoError:
            bytes_string = reply.readAll()
            response = str(bytes_string, 'utf-8')
            #print(response)
            refs = [i for i in range(len(response)) if response.startswith('<cp:CadastralParcel gml:id="ES.SDGC.CP.',i)]
            rc = []
            for i in refs:
                rc.append(response[i + len('<cp:CadastralParcel gml:id="ES.SDGC.CP.'): i + len('<cp:CadastralParcel gml:id="ES.SDGC.CP.') + 14])
            print('referencias catastrales WFS: {}'.format(rc))
            polygonPatches = [i for i in range(len(response)) if response.startswith('<gml:PolygonPatch>', i)]
            polygonPatchesEnd = [i for i in range(len(response)) if response.startswith('</gml:PolygonPatch>', i)]
            for index, i in enumerate(polygonPatches):

                i += len('<gml:PolygonPatch>')
                polygon = response[i:polygonPatchesEnd[index]]
                exterior = polygon.find('<gml:exterior>') + len('<gml:exterior>')
                exteriorEnd = polygon.find('</gml:exterior>')
                exteriorRing = polygon[exterior:exteriorEnd]
                posList = exteriorRing.find('<gml:posList') + len('<gml:posList')
                n = exteriorRing[posList:].find('>')
                posList = posList + n + len('>')
                posListEnd = exteriorRing.find('</gml:posList>')
                coordList_ext = exteriorRing[posList:posListEnd]             
                
                interiorRings = [j for j in range(len(polygon)) if polygon.startswith('<gml:interior>', j)]
                interiorRingsEnd = [j for j in range(len(polygon)) if polygon.startswith('</gml:interior>', j)]
                coordList_int = []
                for index1, j in enumerate(interiorRings):
                    j += len('<gml:interior>')
                    interiorRing = polygon[j:interiorRingsEnd[index1]]
                    posList1 = interiorRing.find('<gml:posList') + len('<gml:posList')
                    n = interiorRing[posList1:].find('>')
                    posList1 = posList1 + n + len('>')
                    posList1End = interiorRing.find('</gml:posList>')
                    coordList_int.append(interiorRing[posList1:posList1End])

                self.create_geometry(coordList_ext.split(), coordList_int, rc[index])

            print('Número de parcelas WFS bbox: {}'.format(len(self.wfsElems)))
            if len(self.wfsElems) > 0:
                self.count_NPO()
            if self.finishedRequests > 0: 
                self.display_options()
            else:
                self.finishedRequests +=1
                
        else:
            print('error: {}'.format(er))


    def create_geometry(self, coords_ext, rings_int, rc):
        polygon = []
        listOfPoints = []
        for index, coord in enumerate(coords_ext):
            if not index % 2:
                listOfPoints.append((float(coord),float(coords_ext[index + 1])))
        polygon = [QgsPointXY( pair[0], pair[1] ) for pair in listOfPoints ]
        geometry = QgsGeometry.fromPolygonXY( [polygon] ) 

        if len(rings_int) > 0:
            for ring in rings_int:
                listOfPoints = []
                for index, coord in enumerate(ring.split()):
                    if not index % 2:
                        listOfPoints.append((float(coord),float(ring.split()[index + 1])))
                part = [QgsPointXY( pair[0], pair[1] ) for pair in listOfPoints]
                geometry.addRing(part)
        
        feature = QgsFeature()
        feature.setGeometry(geometry)
        self.wfsElems.append([feature, rc])

    def count_NPO(self):
        self.NPO = []
        geom = None
        for elem in self.elems:
            wkb_type = elem.geometry().wkbType()
            if wkb_type == QgsWkbTypes.MultiPolygon:
                for part in elem.geometry().asMultiPolygon():
                    geom = QgsGeometry.fromPolygonXY(part) if geom == None else geom.combine(QgsGeometry.fromPolygonXY(part) )
            elif wkb_type == QgsWkbTypes.Polygon:
                geom = feat.geometry() if geom == None else geom.combine(feat.geometry())
            
            for feature in self.wfsElems:
                if geom.equals(feature[0].geometry()):
                    self.show_message("C", self.ui.msg_equalGeometries.format(feature[1]))
                if ( (geom.equals(feature[0].geometry()) or geom.overlaps(feature[0].geometry())) and self.NPO.count(feature[1]) == 0 ):
                    self.NPO.append(feature[1])
            geom = None
        print('NPO: {}'.format(self.NPO))
        
        if len(self.NPO) > 0:
            for feat in self.elems:
                wkb_type = feat.geometry().wkbType()
                if wkb_type == QgsWkbTypes.MultiPolygon:
                    for part in feat.geometry().asMultiPolygon():
                        geom = QgsGeometry.fromPolygonXY(part) if geom == None else geom.combine(QgsGeometry.fromPolygonXY(part) )
                elif wkb_type == QgsWkbTypes.Polygon:
                    geom = feat.geometry() if geom == None else geom.combine(feat.geometry())
            
            geom_wfs = None
            for feat in self.wfsElems:
                if self.NPO.count(feat[1]) > 0:
                    print('geometry to merge: {}'.format(feat[1]))
                    geom_wfs = feat[0].geometry() if geom_wfs == None else geom_wfs.combine(feat[0].geometry())
            #print('geom:' + geom.asWkt())
            #print('geom_wfs:'+ geom_wfs.asWkt())
            if not geom.equals(geom_wfs):
                self.show_message("C", self.ui.msg_contourError)
        else:
            print('No se han encontrado las parcelas de origen')


    def display_options(self):
        total = self.ui.Selec.rowCount()
        namespaces = []
        for fil in range(total):
            namespace = self.ui.Selec.cellWidget(fil, 5).currentIndex()
            namespaces.append(namespace)
        LOCAL = namespaces.count(0)
        SDGC = namespaces.count(1)
        if len(self.NPO) == 1 and self.NPP > 1:
            if SDGC == 0:
                output = 'División' if self.ui.Idioma.currentIndex() == 0 else 'Division'
            elif SDGC == 1:
                output = 'Segregación, Subsanación' if self.ui.Idioma.currentIndex() == 0 else 'Segregation, Rectification'
            elif SDGC > 1:
                output = 'NO PERMITIDO'    
        elif len(self.NPO) > 1 and self.NPP == 1:
            if SDGC == 0 and LOCAL == 1:
                output = 'Agrupación' if self.ui.Idioma.currentIndex() == 0 else 'Aggregation'
            if SDGC == 1:
                output = 'Agregación, Subsanación' if self.ui.Idioma.currentIndex() == 0 else 'Aggregation, Rectification'
        elif len(self.NPO) == self.NPP:
            if LOCAL == 0:
                output = 'Subsanación' if self.ui.Idioma.currentIndex() == 0 else 'Rectification'
            elif LOCAL > 0:
                output = 'Subsanación, Reparcelación' if self.ui.Idioma.currentIndex() == 0 else 'Rectification, Reparcelization'
        elif len(self.NPO) != self.NPP:
            output = 'Subsanación, Reparcelación' if self.ui.Idioma.currentIndex() == 0 else 'Rectification, Reparcelization'
        else:
            output = ''
        self.ui.options.setText(output)
        

    def get_rings(self, geom):
        """ Get list of rings of selected polygon """

        exterior_ring = []
        interior_rings = []
        wkb_type = geom.wkbType()
        if wkb_type == QgsWkbTypes.Polygon:
            polygon = geom.asPolygon()
            exterior_ring = polygon[0]

        elif wkb_type == QgsWkbTypes.MultiPolygon:
            list_polygons = geom.asMultiPolygon()
            polygon = list_polygons[0]
            exterior_ring = polygon[0]
            if len(polygon) > 1:
                for index, ring in enumerate(polygon):
                    if index > 0:
                        interior_rings.append(ring)

        return [exterior_ring, interior_rings]

    def get_points(self, ring):
        """ Get list of points of selected ring """

        punL = ""
        punN = len(ring)
        for point in ring:
            if punL != "":
                punL += " "
            punL += str(format(point.x(), "f")) + " " + str(format(point.y(), "f"))

        return [punN, punL]


    def validate_features_layer(self):
        """ Validate selected features of active layer """

        self.layer = self.iface.activeLayer()
        if not self.layer:
            self.show_message("C", self.ui.msg_noLayer)
            return False
        elif not self.layer.type() == QgsMapLayer.VectorLayer:
            self.show_message("C", self.ui.msg_noVector)
            return False

        self.elems = list(sorted(self.layer.selectedFeatures(), key = lambda feature: feature.geometry().area(), reverse=True))
        ne = len(self.elems)
        if ne == 0:
            self.show_message("C", self.ui.msg_noPolygon)
            return False

        self.crs = self.layer.crs().authid()
        if self.crs.split(':')[0] != 'EPSG':
            self.show_message("C", self.ui.msg_noValidCRS)
            return False

        # Check geometry type
        features = self.layer.selectedFeatures()
        for feature in features:
            geom = feature.geometry()
            if geom.type() != QgsWkbTypes.PolygonGeometry:
                self.show_message("W", self.ui.msg_noPolygonSelected)
                return False
            else:
                return True


    def run(self):
        # Validate selected features of active layer
        if not self.validate_features_layer():
            return

        # Validate layer fields
        nRef = ""
        if self.layer.fields().indexFromName("REFCAT") != -1:
            nRef = "REFCAT"
        elif self.layer.fields().indexFromName("refcat") != -1:
            nRef = "refcat"
        elif self.layer.fields().indexFromName("nationalCadastralReference") != -1:
            nRef = "nationalCadastralReference"
        elif self.layer.fields().indexFromName("nationalCa") != -1:
            nRef = "nationalCa"
        elif self.layer.fields().indexFromName("localId") != -1:
            nRef = "localId"

        # Load form list
        self.ui.data.setDateTime(QDateTime.currentDateTime())
        self.ui.Selec.clear()
        self.ui.Selec.setColumnCount(0)
        self.ui.Selec.setRowCount(0)
        numCols = 6
        self.ui.Selec.setColumnCount(numCols)
        for col in range(numCols):
            self.ui.Selec.setColumnWidth(col, int(str("20,120,80,120,60,80").split(",")[col]))

        self.ui.Selec.setHorizontalHeaderLabels(["S", "RefCat", "Conservar", "LocalId", "Area", "Namespace"])
        self.ui.Selec.horizontalHeader().setFrameStyle(QFrame.Box | QFrame.Plain)
        self.ui.Selec.horizontalHeader().setLineWidth(1)

        self.geo = []
        fil = -1
        refs = []
        for index, elem in enumerate(self.elems):
            self.geo.append(elem.geometry())

            localId = string.ascii_uppercase[index]
            area = int(elem.geometry().area())
            ref = ""
            if nRef != "":
                ref = elem[nRef]

            fil += 1
            self.ui.Selec.setRowCount(fil+1)
            self.ui.Selec.setItem(fil, 0, QTableWidgetItem(str(fil)))
            
            if ref != "":
                if ref not in refs:
                    self.ui.Selec.setItem(fil, 1, QTableWidgetItem(str(ref)))
                    refs.append(ref)
                else:
                    self.ui.Selec.setItem(fil, 1, QTableWidgetItem('NuevaRefCat_' + str(index)))
            else:
                self.ui.Selec.setItem(fil, 1, QTableWidgetItem(""))

            cell_widget = Widget()
            self.ui.Selec.setCellWidget(fil, 2, cell_widget)

            self.ui.Selec.setItem(fil, 3, QTableWidgetItem(str(localId)))
            c = QTableWidgetItem(str(area))
            c.setTextAlignment(Qt.AlignRight)
            self.ui.Selec.setItem(fil, 4, c)
            self.ui.Selec.item(fil, 4).setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            cb1 = QComboBox()
            cb1.addItems(['LOCAL', 'SDGC'])
            self.ui.Selec.setCellWidget(fil, 5, cb1)
            ref = self.ui.Selec.item(fil,1).text()
            if nRef.startswith("nationalCa") and len(ref) == 14:
                self.ui.Selec.cellWidget(fil, 2).setChecked(True)
                self.ui.Selec.setItem(fil, 3, QTableWidgetItem(str(ref)))
                self.ui.Selec.cellWidget(fil, 5).setCurrentIndex(1)
            else:    
                self.ui.Selec.cellWidget(fil, 2).setChecked(False)
                
        self.ui.Selec.resizeRowsToContents()
        if self.ui.desti.text().strip() == "":
            if self.project_dir != "":
                self.ui.desti.setText(self.project_dir)
            else:
                self.ui.desti.setText(self.plugin_dir)
        self.ui.Inspire4.setChecked(True)
        self.ui.check.setChecked(True)
        self.show()

class Widget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.chk_box = QCheckBox()
        self.chk_box.setCheckState(Qt.Unchecked)
        hlayout = QHBoxLayout(self)
        hlayout.addWidget(self.chk_box)
        hlayout.setAlignment(Qt.AlignCenter)
        hlayout.setContentsMargins(0, 0, 0, 0)

    def isChecked(self):
        return self.chk_box.isChecked()

    def setChecked(self, checked):
        self.chk_box.setChecked(checked)
