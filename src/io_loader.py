import SimpleITK as sitk
import numpy as np
import os

def cargar_segmentacion(ruta_archivo):
    """
    Carga un archivo de segmentación médica (NRRD, NIfTI) y extrae sus datos.
    
    Args:
        ruta_archivo (str): La ruta completa al archivo (ej: 'data/mi_tumor.nrrd')
        
    Returns:
        dict: Un diccionario con:
            - "array": La matriz de numpy (Z, Y, X) con la máscara.
            - "spacing": El tamaño del vóxel en mm (x, y, z).
            - "origin": La coordenada de origen en el espacio (x, y, z).
            - "sitk_obj": El objeto original (útil para guardar después).
            Retorna None si hay error.
    """
    
    # 1. Verificar si el archivo existe
    if not os.path.exists(ruta_archivo):
        print(f"[ERROR] No se encontró el archivo: {ruta_archivo}")
        return None

    print(f"--- Cargando: {os.path.basename(ruta_archivo)} ---")
    
    try:
        # 2. Leer la imagen usando el estándar médico
        imagen = sitk.ReadImage(ruta_archivo)
        
        # 3. Extraer información física (Vital para Radioterapia)
        spacing = imagen.GetSpacing() # Tamaño del píxel
        origin = imagen.GetOrigin()   # Coordenadas mundo
        
        # 4. Convertir la imagen a matriz de números (NumPy)
        # Nota: SimpleITK usa orden (x,y,z), NumPy usa (z,y,x).
        array_data = sitk.GetArrayFromImage(imagen)
        
        print(f" -> Dimensiones matriz: {array_data.shape}")
        print(f" -> Vóxel spacing (mm): {spacing}")
        
        return {
            "array": array_data,
            "spacing": spacing,
            "origin": origin,
            "sitk_obj": imagen
        }

    except Exception as e:
        print(f"[ERROR CRÍTICO] Fallo al leer la imagen: {e}")
        return None