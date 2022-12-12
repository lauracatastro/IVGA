# -*- coding: utf-8 -*-
from PyQt5 import QtNetwork
from PyQt5.QtCore import Qt, QCoreApplication, QDateTime, QCoreApplication, QUrl
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QDialog, QAction, QMessageBox, QFileDialog, QTableWidgetItem, QFrame, QComboBox
from qgis.core import QgsProject, QgsWkbTypes, QgsMapLayer
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
        self.ui.Carpeta.setIcon(QIcon(self.manage_slash(self.plugin_dir + "/folder.png")))
        self.ui.Carpeta.clicked.connect(self.select_folder)
        self.ui.Crear.clicked.connect(self.create_gml)
        self.ui.Tancar.clicked.connect(self.close)


    def unload(self):

        # Remove icons and actions
        self.iface.removePluginMenu(self.tr(u'&IVGA'),self.action)
        self.iface.removeToolBarIcon(self.action)
        self.iface.newProjectCreated.disconnect(self.change_project)
        self.iface.projectRead.disconnect(self.change_project)
        self.ui.Carpeta.clicked.disconnect(self.select_folder)
        self.ui.Crear.clicked.disconnect(self.create_gml)
        self.ui.Tancar.clicked.disconnect(self.close)
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
            self.check_refs()
        else:
            self.write_gml()
        

    def write_gml(self):
        iv = 3
        if self.ui.Inspire4.isChecked():
            iv = 4

         # Check filename
        filename = str(self.ui.fileName.text())
        if filename == "":
            msg = "Debe definir el nombre del fichero"
            if self.show_message("W", msg) == QMessageBox.Ok:
                return
        else:
            f = self.manage_slash(self.ui.desti.text() + "/" + filename + ".gml")
            if os.path.exists(f):
                msg = "El fichero " + filename + ".gml ya existe\n\n¿Desea reemplazarlo?"
                if self.show_message("P", msg) == QMessageBox.No:
                    return


        total = self.ui.Selec.rowCount()
        for fil in range(total):
            ref = self.ui.Selec.item(fil, 1).text()
                     
            area = self.ui.Selec.item(fil, 3).text()
            namespace = self.ui.Selec.cellWidget(fil, 4).currentText()
            localId = ""
            if ref != "" and len(ref) == 14 and namespace == 'SDGC':
                localId = ref
            else:
                localId = self.ui.Selec.item(fil, 2).text()


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
        
        self.show_message("M", "Archivo GML creado en la carpeta destino: \n" + filename + ".gml")


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
            z+='<FeatureCollection ' ## COMENTARIO D.G. del Catastro: El namespace "wfs:" no se admite en la validación de esta etiqueta
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
            
            ## COMENTARIO D.G. del Catastro: Debemos añadir los anillos interiores al GML para parcelas con huecos
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
            z='<member>\n' ## COMENTARIO D.G. del Catastro: El namespace "wfs:" no se admite en la validación de esta etiqueta
            z+='<cp:CadastralParcel gml:id="ES.'+namespace+'.CP.'+str(localId)+'">\n'
            z+='<cp:areaValue uom="m2">'+str(area)+'</cp:areaValue>\n'

            ## COMENTARIO D.G. del Catastro: Etiquetas necesarias para el esquema, aunque sean nulas:
            z+='<cp:beginLifespanVersion xsi:nil="true" nilReason="http://inspire.ec.europa.eu/codelist/VoidReasonValue/Unpopulated"></cp:beginLifespanVersion>\n'
            z+='<cp:endLifespanVersion xsi:nil="true" nilReason="http://inspire.ec.europa.eu/codelist/VoidReasonValue/Unpopulated"></cp:endLifespanVersion>\n'

            z+='<cp:geometry>\n'
            z+='<gml:MultiSurface gml:id="MultiSurface_ES.'+namespace+'.CP.'+str(localId)+'" srsName="http://www.opengis.net/def/crs/EPSG/0/'+str(epsg)+'">\n'
            z+='<gml:surfaceMember>\n'
            z+='<gml:Surface gml:id="Surface_ES.'+namespace+'.CP.'+str(localId)+'.1" srsName="http://www.opengis.net/def/crs/EPSG/0/'+str(epsg)+'">\n'
            z+='<gml:patches>\n<gml:PolygonPatch>'

            ## COMENTARIO D.G. del Catastro: Debemos añadir los anillos interiores al GML para parcelas con huecos
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
            z+='</member>\n' ## COMENTARIO D.G. del Catastro: El namespace "wfs:" no se admite en la validación de esta etiqueta

        return z


    def footer_gml(self,v) :
        """ GML footer """

        if v == 3:
            z = '</gml:FeatureCollection>\n'
        else:
            z = '</FeatureCollection>\n' ## COMENTARIO D.G. del Catastro: El namespace "wfs:" no se admite en la validación de esta etiqueta

        return z



    def check_refs(self):
        total = self.ui.Selec.rowCount()
        self.refsToCheck = []
        self.notFound = []
        for fil in range(total):
            ref = self.ui.Selec.item(fil, 1).text().upper()
            if len(ref) == 14 :
                self.refsToCheck.append([ref,fil])
            else:
                self.ui.Selec.cellWidget(fil, 4).setCurrentIndex(0)

        self.manager = QtNetwork.QNetworkAccessManager()
        self.manager.finished.connect(self.handleResponse)
        ## COMENTARIO D.G. del Catastro: Definimos QNetworkAccessManager fuera del bucle para no sobreescribir la petición
        if len(self.refsToCheck) > 0:
            for item in self.refsToCheck:
                url = 'http://ovc.catastro.meh.es/INSPIRE/wfsCP.aspx?service=wfs&version=2&request=getfeature&STOREDQUERIE_ID=GetParcel&refcat={}&srsname=EPSG::{}'.format(item[0],str(self.crs.split(":")[1]))
                req = QtNetwork.QNetworkRequest(QUrl(url))
                self.manager.get(req)
        else:
            self.write_gml()

    def handleResponse(self, reply):
        er = reply.error()
        if er == QtNetwork.QNetworkReply.NetworkError.NoError:
            bytes_string = reply.readAll()
            response = str(bytes_string, 'utf-8')
            print(response)

            if 'Exception' in response:
                start = response.index('<ExceptionText><![CDATA[No se ha encontrado la parcela ') + len('<ExceptionText><![CDATA[No se ha encontrado la parcela ')
                end = start + 14
                ref = response[start:end]
                self.notFound.append(ref)
                for i in range(len(self.refsToCheck)):
                    if self.refsToCheck[i][0] == ref:    
                        fil = self.refsToCheck[i][1]
                        self.ui.Selec.item(fil, 2).setText(string.ascii_uppercase[fil])
                        self.ui.Selec.cellWidget(fil, 4).setCurrentIndex(0)
            elif 'cp:CadastralParcel' in response:
                start = response.index('<localId>') + len('<localId>')
                end = start + 14
                ref = response[start:end]
                for i in range(len(self.refsToCheck)):
                    if self.refsToCheck[i][0] == ref:    
                        fil = self.refsToCheck[i][1]
                        self.ui.Selec.item(fil, 2).setText(ref) ## COMENTARIO D.G. del Catastro: LocalId = ref
                        self.ui.Selec.cellWidget(fil, 4).setCurrentIndex(1)

            if fil == self.refsToCheck[-1][1]:
                if len(self.notFound) > 0 :
                    msg = "Las Referencias Catastrales siguientes no se encuentran en Catastro:"
                    for ref in self.notFound:
                        msg += '\n' + ref
                    self.show_message("W", msg)
                self.write_gml()

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
        self.isVectorLayer = (self.layer.type() == QgsMapLayer.VectorLayer)
        if not self.layer:
            self.show_message("C", "No hay ninguna capa activa")
            return False
        elif not self.isVectorLayer:
            self.show_message("C", "La capa activa debe ser de tipo vectorial")
            return False

        self.elems = list(sorted(self.layer.selectedFeatures(), key = lambda feature: feature.geometry().area(), reverse=True))
        ne = len(self.elems)
        if ne == 0:
            self.show_message("C", "Debe seleccionar como mínimo una parcela")
            return False

        self.crs = self.layer.crs().authid()
        if self.crs.split(':')[0] != 'EPSG':
            self.show_message("C", "La capa activa no utiliza un sistema de coordenadas compatible")
            return False

        # Check geometry type
        features = self.layer.selectedFeatures()
        for feature in features:
            geom = feature.geometry()
            if geom.type() != QgsWkbTypes.PolygonGeometry:
                msg = "La capa seleccionada no es de tipo polígono"
                self.show_message("W", msg)
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
            ## COMENTARIO D.G. del Catastro: al importar un GML en QGIS el nombre del campo se corta
            nRef = "nationalCa"
        elif self.layer.fields().indexFromName("localId") != -1:
            nRef = "localId"

        # Load form list
        self.ui.data.setDateTime(QDateTime.currentDateTime())
        self.ui.Selec.clear()
        self.ui.Selec.setColumnCount(0)
        self.ui.Selec.setRowCount(0)
        numCols = 5
        self.ui.Selec.setColumnCount(numCols)
        for col in range(numCols):
            self.ui.Selec.setColumnWidth(col, int(str("20,120,120,60,80").split(",")[col]))

        ## COMENTARIO D.G. del Catastro: Añadimos opción de Namespace, que se seleccionará dependiendo de la operación que se necesite hacer
        self.ui.Selec.setHorizontalHeaderLabels(["S", "RefCat", "LocalId", "Area", "Namespace"])
        self.ui.Selec.horizontalHeader().setFrameStyle(QFrame.Box | QFrame.Plain)
        self.ui.Selec.horizontalHeader().setLineWidth(1)

        self.geo = []
        fil = -1
        refs = []
        for index, elem in enumerate(self.elems):
            self.geo.append(elem.geometry())

            ## COMENTARIO D.G. del Catastro: Rellenamos un valor diferente para cada parcela seleccionada
            localId = string.ascii_uppercase[index]
            ## COMENTARIO D.G. del Catastro: Rellenamos siempre con el área calculada para la geometría
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

            self.ui.Selec.setItem(fil, 2, QTableWidgetItem(str(localId)))
            c = QTableWidgetItem(str(area))
            c.setTextAlignment(Qt.AlignRight)
            self.ui.Selec.setItem(fil, 3, c)
            self.ui.Selec.item(fil, 3).setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            cb = QComboBox()
            cb.addItems(['LOCAL', 'SDGC'])
            self.ui.Selec.setCellWidget(fil, 4, cb)
            ref = self.ui.Selec.item(fil,1).text()
            if nRef.startswith("nationalCa") and len(ref) == 14:
                self.ui.Selec.setItem(fil, 2, QTableWidgetItem(str(ref)))
                self.ui.Selec.cellWidget(fil, 4).setCurrentIndex(1)
                
        self.ui.Selec.resizeRowsToContents()
        if self.ui.desti.text().strip() == "":
            if self.project_dir != "":
                self.ui.desti.setText(self.project_dir)
            else:
                self.ui.desti.setText(self.plugin_dir)
        self.ui.Inspire4.setChecked(True)
        self.ui.check.setChecked(True)
        self.show()

