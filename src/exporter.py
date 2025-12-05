import SimpleITK as sitk
import numpy as np

def distancia_punto_segmento(punto, a, b):
    """
    Calcula la distancia mínima desde un punto P al segmento de línea A-B.
    """
    vec_ab = b - a
    vec_ap = punto - a
    
    # Proyección del punto sobre la línea (valor t entre 0 y 1)
    len_sq = np.dot(vec_ab, vec_ab)
    if len_sq == 0: return np.linalg.norm(vec_ap) # A y B son el mismo punto
    
    t = np.dot(vec_ap, vec_ab) / len_sq
    t = np.clip(t, 0.0, 1.0) # Restringir al segmento
    
    # Punto más cercano en el segmento
    closest = a + t * vec_ab
    return np.linalg.norm(punto - closest)

def exportar_nrrd_completo(ruta_salida, esferas, cilindros, datos_ref, r_esfera=3.0, r_cilindro=1.5):
    """
    Genera un único archivo NRRD con:
    - Etiqueta 1: Esferas
    - Etiqueta 2: Cilindros
    """
    print(f"--- Exportando solución completa a: {ruta_salida} ---")
    
    shape = datos_ref["array"].shape  # (z, y, x)
    spacing = datos_ref["spacing"]
    origin = datos_ref["origin"]
    
    # Matriz vacía
    matriz_salida = np.zeros(shape, dtype=np.uint8)
    
    # --- 1. QUEMAR CILINDROS (Etiqueta 2) ---
    # Lo hacemos primero para que si hay solapamiento accidental, la esfera (1) prevalezca después
    print(f" -> Rasterizando {len(cilindros)} estructuras de control (Label 2)...")
    
    # Margen de búsqueda en píxeles (radio cilindro + 1)
    rad_pix = int(np.ceil(r_cilindro / min(spacing))) + 1
    
    for p1, p2 in cilindros:
        # Definir Bounding Box del cilindro para no recorrer toda la matriz
        min_p = np.minimum(p1, p2) - r_cilindro
        max_p = np.maximum(p1, p2) + r_cilindro
        
        # Convertir a índices
        min_idx = np.round((min_p - origin) / spacing).astype(int)
        max_idx = np.round((max_p - origin) / spacing).astype(int)
        
        # Clampear índices dentro de la imagen
        min_k = max(0, min_idx[2]); max_k = min(shape[0], max_idx[2] + 1)
        min_j = max(0, min_idx[1]); max_j = min(shape[1], max_idx[1] + 1)
        min_i = max(0, min_idx[0]); max_i = min(shape[2], max_idx[0] + 1)
        
        # Iterar en la caja
        for k in range(min_k, max_k):
            z_coord = origin[2] + k * spacing[2]
            for j in range(min_j, max_j):
                y_coord = origin[1] + j * spacing[1]
                for i in range(min_i, max_i):
                    x_coord = origin[0] + i * spacing[0]
                    
                    punto_actual = np.array([x_coord, y_coord, z_coord])
                    
                    # Calcular distancia matemática al eje del cilindro
                    dist = distancia_punto_segmento(punto_actual, p1, p2)
                    
                    if dist <= r_cilindro:
                        matriz_salida[k, j, i] = 2  # ETIQUETA 2 = CILINDRO

    # --- 2. QUEMAR ESFERAS (Etiqueta 1) ---
    print(f" -> Rasterizando {len(esferas)} esferas (Label 1)...")
    rad_pix_esf = int(np.ceil(r_esfera / min(spacing))) + 1
    
    for centro in esferas:
        cx = int((centro[0] - origin[0]) / spacing[0])
        cy = int((centro[1] - origin[1]) / spacing[1])
        cz = int((centro[2] - origin[2]) / spacing[2])
        
        # Bounding Box Esfera
        min_k = max(0, cz - rad_pix_esf); max_k = min(shape[0], cz + rad_pix_esf + 1)
        min_j = max(0, cy - rad_pix_esf); max_j = min(shape[1], cy + rad_pix_esf + 1)
        min_i = max(0, cx - rad_pix_esf); max_i = min(shape[2], cx + rad_pix_esf + 1)
        
        for k in range(min_k, max_k):
            pz = origin[2] + k * spacing[2]
            for j in range(min_j, max_j):
                py = origin[1] + j * spacing[1]
                for i in range(min_i, max_i):
                    px = origin[0] + i * spacing[0]
                    
                    dist = np.sqrt((px-centro[0])**2 + (py-centro[1])**2 + (pz-centro[2])**2)
                    if dist <= r_esfera:
                        matriz_salida[k, j, i] = 1 # ETIQUETA 1 = ESFERA (Sobrescribe cilindro si tocase)

    # 3. Guardar
    img_sitk = sitk.GetImageFromArray(matriz_salida)
    img_sitk.SetSpacing(spacing)
    img_sitk.SetOrigin(origin)
    # Copiamos dirección original para mantener orientación del paciente
    img_sitk.SetDirection(datos_ref["sitk_obj"].GetDirection())
    
    sitk.WriteImage(img_sitk, ruta_salida)
    print(" -> Archivo guardado correctamente.")