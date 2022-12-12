# IVGA: DOCUMENTATION / DOCUMENTACIÓN
**ENGLISH:** 

**_Creation of GML file to validate cadastral parcel_**

The requirements for this plugin to work are:
- The active layer must be a vector layer
- There must be at least one selected feature of type Polygon or MultiPolygon

If either of those conditions are not met, the plugin will throw an error message indicating the cause.

The user interface when the plugin opens:

![image](https://user-images.githubusercontent.com/101393679/207062519-9c302dc4-05a3-4b0c-b030-e04c3452e792.png)

1. Title: It contains an hyperlink redirecting to the official documentation for the IVGA proccedure.
2. Selected Parcels: 
    
    It shows a table with the following information about the selected polygons (Cadastral Parcels -CP-):
    - S: order of selection for the polygon
    - RefCat: Cadastral Refference
    - LocalId: Corresponding to the polygon's GML LocalId, there must be a unique identifier for each CP
    - Area: Geometrically calculated area in m<sup>2</sup>. This field is locked.
    - Namespace: Corresponding to the LocalId namespace. If the LocalId already exists in the Spanish Cadastre this must be SDGC, otherwise it should me LOCAL
3. Check Ref. Cat.:
    
    If this checkbox is checked, it will make a request to the Spanish Cadastre for each RefCat with 14 characters, the RefCat exists:
    - LocalId changes to the same as RefCat
    - Namespace changes to SDGC
    
    In any other case:
    - LocalId is a new unique identifier
    - Namespace is LOCAL
    
    This is very important, every combination of namespaces in the GML outputs a different IVG proccedure:
    
    ![image](https://user-images.githubusercontent.com/101393679/207037468-e1f3aef0-b501-4485-933f-bb615374af31.png)
 4. File name without extension
 5. Timestamp / Inspire CP output GML version (version 4 is default, as the system checks from this version backwards)
 6. Destination folder
 7. Save GML / Close




**SPANISH:**

**_Creación de fichero GML para validar parcela catastral_**

Los requisitos para el funcionamiento del plugin son los siguientes:
- La capa activa debe ser de tipo vectorial
- Debe seleccionarse al menos un elemento de tipo polígono o multipolígono

Si no se cumple alguna de las condiciones, se mostrará un mensaje de error indicando la causa.

La interfaz de usuario al abrir el plugin se muestra a continuación:

![image](https://user-images.githubusercontent.com/101393679/207062519-9c302dc4-05a3-4b0c-b030-e04c3452e792.png)

1. Título: Contiene un hipervínculo redirigiendo a la documentación oficial del procedimiento IVGA.
2. Parcelas seleccionadas:
    
    Muestra una tabla con la siguiente información de los polígons seleccionados (parcelas catastrales):
    - S: Orden de selección del polígono
    - RefCat: Referencia Catastral
    - LocalId: Corresponde al LocalId del polígono dentro del GML. Debe haber un identificador único para cada polígono.
    - Area: Superficie calculada geométricamente en m<sup>2</sup>. Este campo no se puede editar.
    - Namespace: Corresponde al namespace para el localId. Si el localId existe en el Catastro, este campo debe ser SDGC, en caso contrario debería ser LOCAL
 4. Comprobar Ref.Cat.:
    
    Si se selecciona esta opción, se hará una petición a Catastro para cada RefCat de 14 caracteres, si existe:
    - LocalId cambia para ser igual que RefCat
    - Namespace cambia a SDGC
    
    En cualquier otro caso:
    - LocalId sería un identificador único generado automáticamente
    - Namespace sería LOCAL
    
    Esto es importante debido a que cada combinación de namespaces en el GML permite diferentes tipos de procedimientos:
    
    ![image](https://user-images.githubusercontent.com/101393679/207037468-e1f3aef0-b501-4485-933f-bb615374af31.png)
5. Nombre del fichero de salida, sin extensión
6. Fecha y hora / Versión Inspire del GML de salida (por defecto versión 4, ya que el sistema comprueba desde la versión 4 hacia atrás)
6. Carpeta de destino
7. Crear GML / Salir
