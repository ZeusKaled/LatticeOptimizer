import os
import sys
import numpy as np
import SimpleITK as sitk

# Truco para importar módulos desde la carpeta 'src'
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from io_loader import cargar_segmentacion

def crear_gtv_dummy(ruta_salida):
    """Crea un cubo simple de prueba si no existe archivo real."""
    print("[SETUP] Creando GTV sintético de prueba...")
    # Crear cubo de 100x100x100
    arr = np.zeros((100, 100, 100), dtype=np.uint8)
    # Pintar un "tumor" cuadrado en el centro
    arr[30:70, 30:70, 30:70] = 1
    
    img = sitk.GetImageFromArray(arr)
    img.SetSpacing((1.0, 1.0, 1.0)) # 1mm por vóxel
    sitk.WriteImage(img, ruta_salida)
    print(f"[SETUP] Archivo guardado en: {ruta_salida}")

def main():
    # --- CONFIGURACIÓN ---
    archivo_gtv = os.path.join("data", "GTV.nrrd")
    
    # 1. Verificar si existen datos. Si no, crear falsos.
    if not os.path.exists(archivo_gtv):
        print(f"[AVISO] No se encontró '{archivo_gtv}'.")
        crear_gtv_dummy(archivo_gtv)

    # 2. Usar nuestro módulo de carga
    datos = cargar_segmentacion(archivo_gtv)
    
    if datos:
        # Calcular volumen simple (Vóxeles * volumen de 1 vóxel)
        # spacing es (x, y, z), su producto es el volumen de 1 vóxel
        voxel_vol = np.prod(datos["spacing"]) 
        num_voxeles = np.sum(datos["array"])
        vol_cc = (num_voxeles * voxel_vol) / 1000.0 # Convertir mm3 a cc
        
        print(f"\n[ÉXITO] El sistema funciona.")
        print(f" -> Volumen del GTV detectado: {vol_cc:.2f} cc")
        print(" -> Siguiente paso: Generar puntos dentro de este volumen.")

if __name__ == "__main__":
    main()