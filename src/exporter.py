import SimpleITK as sitk
import numpy as np

def exportar_nrrd(ruta_salida, esferas, datos_ref, radio_mm=5.0):
    """
    Genera un archivo NRRD (LabelMap) con las esferas dibujadas.
    
    Args:
        ruta_salida (str): Donde guardar el archivo (ej: 'output/Lattice_Plan.nrrd').
        esferas (np.array): Coordenadas (N, 3) de los centros de las esferas.
        datos_ref (dict): El diccionario del GTV original (para copiar origen y spacing).
        radio_mm (float): Radio de las esferas a dibujar.
    """
    print(f"--- Exportando resultados a: {ruta_salida} ---")
    
    # 1. Recuperar metadatos del GTV original
    shape = datos_ref["array"].shape  # (z, y, x)
    spacing = datos_ref["spacing"]    # (sx, sy, sz)
    origin = datos_ref["origin"]      # (ox, oy, oz)
    
    # 2. Crear una matriz vacía (toda ceros) del mismo tamaño que el GTV
    # Usamos uint8 porque será una máscara (0 = nada, 1 = esfera)
    matriz_salida = np.zeros(shape, dtype=np.uint8)
    
    print(f" -> 'Quemando' {len(esferas)} esferas en el volumen 3D...")
    
    # 3. Dibujar cada esfera en la matriz
    # Para hacerlo eficiente, no revisamos toda la matriz, solo una caja alrededor de la esfera.
    
    # Radio en píxeles (aprox) para saber cuánto buscar
    rad_pix_x = int(radio_mm / spacing[0]) + 1
    rad_pix_y = int(radio_mm / spacing[1]) + 1
    rad_pix_z = int(radio_mm / spacing[2]) + 1
    
    for centro in esferas:
        # Convertir coordenada física (mm) a índice de matriz (i, j, k)
        cx = int((centro[0] - origin[0]) / spacing[0])
        cy = int((centro[1] - origin[1]) / spacing[1])
        cz = int((centro[2] - origin[2]) / spacing[2])
        
        # Definir los límites de la caja de búsqueda (bounding box)
        # np.clip asegura que no nos salgamos de la imagen
        min_k = max(0, cz - rad_pix_z)
        max_k = min(shape[0], cz + rad_pix_z + 1)
        
        min_j = max(0, cy - rad_pix_y)
        max_j = min(shape[1], cy + rad_pix_y + 1)
        
        min_i = max(0, cx - rad_pix_x)
        max_i = min(shape[2], cx + rad_pix_x + 1)
        
        # Iterar solo en la cajita alrededor del centro
        for k in range(min_k, max_k):
            for j in range(min_j, max_j):
                for i in range(min_i, max_i):
                    
                    # Calcular posición física de este vóxel actual
                    px = origin[0] + i * spacing[0]
                    py = origin[1] + j * spacing[1]
                    pz = origin[2] + k * spacing[2]
                    
                    # Distancia al centro de la esfera
                    dist = np.sqrt((px-centro[0])**2 + (py-centro[1])**2 + (pz-centro[2])**2)
                    
                    if dist <= radio_mm:
                        matriz_salida[k, j, i] = 1

    # 4. Convertir matriz NumPy a Imagen SimpleITK
    img_sitk = sitk.GetImageFromArray(matriz_salida)
    
    # 5. IMPORTANTE: Copiar los metadatos físicos de la imagen original
    # Si no hacemos esto, Slicer no sabrá donde poner las esferas.
    img_sitk.SetSpacing(spacing)
    img_sitk.SetOrigin(origin)
    # Copiamos también la dirección (rotación del paciente)
    img_sitk.SetDirection(datos_ref["sitk_obj"].GetDirection())
    
    # 6. Guardar archivo
    sitk.WriteImage(img_sitk, ruta_salida)
    print(" -> Archivo guardado correctamente.")