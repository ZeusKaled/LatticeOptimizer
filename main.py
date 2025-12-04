import os
import sys
import numpy as np
import SimpleITK as sitk

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# IMPORTAMOS NUESTROS DOS MÓDULOS
from io_loader import cargar_segmentacion
from grid_generator import generar_grilla_candidatos  # <--- NUEVO

def crear_gtv_dummy(ruta_salida):
    """Crea un cubo simple de prueba si no existe archivo real."""
    print("[SETUP] Creando GTV sintético de prueba...")
    arr = np.zeros((100, 100, 100), dtype=np.uint8)
    arr[30:70, 30:70, 30:70] = 1 # Tumor central
    img = sitk.GetImageFromArray(arr)
    img.SetSpacing((1.0, 1.0, 1.0))
    sitk.WriteImage(img, ruta_salida)

def main():
    # --- CONFIGURACIÓN ---
    archivo_gtv = os.path.join("data", "GTV.nrrd")
    
    if not os.path.exists(archivo_gtv):
        crear_gtv_dummy(archivo_gtv)

    # 1. Cargar datos
    datos = cargar_segmentacion(archivo_gtv)
    
    if datos:
        # 2. Generar Grilla de Puntos
        # Usamos un paso de 3.0 mm (puedes cambiarlo)
        puntos_candidatos = generar_grilla_candidatos(datos, paso_mm=3.0)
        
        # Muestra simple de los primeros 3 puntos para verificar
        print("\n[RESULTADO]")
        print(f" -> Total candidatos generados: {len(puntos_candidatos)}")
        if len(puntos_candidatos) > 0:
            print(f" -> Ejemplo coords punto 0: {puntos_candidatos[0]}")
        
        print(" -> Listo para la fase de Optimización.")

if __name__ == "__main__":
    main()