import os
import sys
import numpy as np
import SimpleITK as sitk

# --- ARREGLO DE IMPORTACIÓN ---
ruta_src = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.append(ruta_src)

try:
    from io_loader import cargar_segmentacion
    from optimizer import generar_lattice_cubico, generar_cilindros_control
    from visualizer import visualizar_lattice_control
    from exporter import exportar_nrrd_completo # <--- IMPORTAMOS LA NUEVA FUNCIÓN
except ImportError as e:
    print(f"[ERROR IMPORTS] {e}")
    sys.exit(1)

def crear_gtv_grande(ruta_salida):
    print("[SETUP] Generando GTV Grande...")
    size = 130
    arr = np.zeros((size, size, size), dtype=np.uint8)
    z, y, x = np.ogrid[:size, :size, :size]
    centro = (65, 65, 65)
    mascara = ((x - centro[0])**2 + (y - centro[1])**2 + (z - centro[2])**2) <= 40.0**2
    arr[mascara] = 1
    img = sitk.GetImageFromArray(arr)
    img.SetSpacing((1.0, 1.0, 1.0))
    sitk.WriteImage(img, ruta_salida)

def main():
    archivo_gtv = os.path.join("data", "GTV.nrrd")
    carpeta_salida = "output"
    if not os.path.exists(carpeta_salida): os.makedirs(carpeta_salida)

    if not os.path.exists(archivo_gtv):
        crear_gtv_grande(archivo_gtv)
    else:
        img = sitk.ReadImage(archivo_gtv)
        if img.GetSize()[0] < 120:
            crear_gtv_grande(archivo_gtv)

    # 1. Cargar
    datos = cargar_segmentacion(archivo_gtv)

    # --- PARÁMETROS ---
    spacing_lat = 15.0  
    r_esfera = 4.0      
    r_cilindro = 1.5    
    gap_seguridad = 1.5

    # 2. Generar Geometría
    esferas = generar_lattice_cubico(datos, espaciamiento_red_mm=spacing_lat)
    cilindros = generar_cilindros_control(esferas, spacing_lat, r_esfera, gap_mm=gap_seguridad)
    
    print(f"\n[RESUMEN] Esferas: {len(esferas)} | Cilindros: {len(cilindros)}")
    
    if len(esferas) > 0:
        # 3. Exportar Archivo Único (Rasterizado)
        ruta_resultado = os.path.join(carpeta_salida, "Lattice_Solution.nrrd")
        
        # Esta función puede tardar unos segundos porque calcula vóxel a vóxel
        exportar_nrrd_completo(ruta_resultado, esferas, cilindros, datos, r_esfera, r_cilindro)
        
        # 4. Visualizar
        visualizar_lattice_control(esferas, cilindros, r_esfera, r_cilindro)

if __name__ == "__main__":
    main()