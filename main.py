import os
import sys
import numpy as np
import SimpleITK as sitk

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# IMPORTAR MÓDULOS
from io_loader import cargar_segmentacion
from grid_generator import generar_grilla_candidatos
from optimizer import optimizador_greedy          # <--- NUEVO

def crear_gtv_dummy(ruta_salida):
    """Crea un cubo simple de prueba."""
    print("[SETUP] Creando GTV sintético de prueba...")
    arr = np.zeros((100, 100, 100), dtype=np.uint8)
    arr[30:70, 30:70, 30:70] = 1 # Tumor de 40mm x 40mm x 40mm
    img = sitk.GetImageFromArray(arr)
    img.SetSpacing((1.0, 1.0, 1.0))
    sitk.WriteImage(img, ruta_salida)

def main():
    # --- CONFIGURACIÓN ---
    archivo_gtv = os.path.join("data", "GTV.nrrd")
    
    if not os.path.exists(archivo_gtv):
        crear_gtv_dummy(archivo_gtv)

    # 1. Cargar
    datos = cargar_segmentacion(archivo_gtv)
    
    if datos:
        # 2. Generar Candidatos
        # Usamos paso pequeño (2mm) para tener más opciones de dónde elegir
        candidatos = generar_grilla_candidatos(datos, paso_mm=2.0)
        
        # 3. Optimizar (Seleccionar esferas)
        # Pedimos 10 esferas, separadas al menos 15mm entre sí
        esferas_finales = optimizador_greedy(candidatos, num_esferas=10, distancia_min_mm=15.0)
        
        # RESULTADOS
        print("\n[REPORTE FINAL]")
        print(f" -> Candidatos totales evaluados: {len(candidatos)}")
        print(f" -> Vértices Lattice colocados: {len(esferas_finales)}")
        print(" -> Coordenadas (x, y, z):")
        print(esferas_finales)

if __name__ == "__main__":
    main()