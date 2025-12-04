import os
import sys
import numpy as np
import SimpleITK as sitk

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# IMPORTAR MÓDULOS
from io_loader import cargar_segmentacion
from grid_generator import generar_grilla_candidatos
from optimizer import optimizador_greedy
from visualizer import visualizar_lattice
from exporter import exportar_nrrd  # <--- NUEVO

def crear_gtv_dummy(ruta_salida):
    """Crea un cubo simple de prueba."""
    print("[SETUP] Creando GTV sintético de prueba...")
    arr = np.zeros((100, 100, 100), dtype=np.uint8)
    arr[30:70, 30:70, 30:70] = 1 
    img = sitk.GetImageFromArray(arr)
    img.SetSpacing((1.0, 1.0, 1.0))
    sitk.WriteImage(img, ruta_salida)

def main():
    # --- CONFIGURACIÓN ---
    archivo_gtv = os.path.join("data", "GTV.nrrd")
    
    # Carpeta donde guardaremos el resultado
    carpeta_salida = "output"
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)
    
    if not os.path.exists(archivo_gtv):
        crear_gtv_dummy(archivo_gtv)

    # 1. Cargar
    datos = cargar_segmentacion(archivo_gtv)
    
    if datos:
        # 2. Generar Candidatos
        candidatos = generar_grilla_candidatos(datos, paso_mm=2.0)
        
        # 3. Optimizar (Radio visual 5mm, Distancia 15mm)
        esferas_finales = optimizador_greedy(candidatos, num_esferas=10, distancia_min_mm=15.0)
        
        print(f"\n[RESULTADO] Se colocaron {len(esferas_finales)} esferas.")
        
        if len(esferas_finales) > 0:
            # 4. Exportar (NUEVO)
            ruta_resultado = os.path.join(carpeta_salida, "Lattice_Solution.nrrd")
            exportar_nrrd(ruta_resultado, esferas_finales, datos, radio_mm=5.0)
            
            # 5. Visualizar
            visualizar_lattice(candidatos, esferas_finales, radio_esfera=5.0)
            
        else:
            print("No hay esferas para visualizar ni exportar.")

if __name__ == "__main__":
    main()