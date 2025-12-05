import numpy as np
import SimpleITK as sitk
from scipy.spatial import KDTree

def obtener_indices_fisicos(posicion_fisica, origin, spacing):
    i = int(round((posicion_fisica[0] - origin[0]) / spacing[0]))
    j = int(round((posicion_fisica[1] - origin[1]) / spacing[1]))
    k = int(round((posicion_fisica[2] - origin[2]) / spacing[2]))
    return i, j, k

def verificar_dentro_gtv(punto, mask, origin, spacing, margen_seguridad_mm=5.0):
    i, j, k = obtener_indices_fisicos(punto, origin, spacing)
    z_len, y_len, x_len = mask.shape
    if not (0 <= i < x_len and 0 <= j < y_len and 0 <= k < z_len): return False
    if mask[k, j, i] == 0: return False
    return True

def generar_lattice_cubico(datos_gtv, espaciamiento_red_mm=15.0):
    """Genera vértices (esferas) en red CÚBICA estricta."""
    print(f"--- Generando Red Cúbica (Grid: {espaciamiento_red_mm} mm) ---")
    mask = datos_gtv["array"]
    spacing = datos_gtv["spacing"]
    origin = datos_gtv["origin"]
    
    coords_z, coords_y, coords_x = np.where(mask > 0)
    if len(coords_z) == 0: return np.array([])
    
    centro_gtv = np.array([
        origin[0] + np.mean(coords_x) * spacing[0],
        origin[1] + np.mean(coords_y) * spacing[1],
        origin[2] + np.mean(coords_z) * spacing[2]
    ])
    
    rango_max = 120.0 
    num_pasos = int(rango_max / espaciamiento_red_mm) + 1
    rango = range(-num_pasos, num_pasos + 1)
    
    esferas = []
    for k in rango:
        for j in rango:
            for i in rango:
                pos = centro_gtv + np.array([i, j, k]) * espaciamiento_red_mm
                if verificar_dentro_gtv(pos, mask, origin, spacing, margen_seguridad_mm=2.5):
                    esferas.append(pos)
                    
    return np.array(esferas)

def generar_cilindros_control(esferas, spacing_lattice, radio_esfera, gap_mm=2.0):
    """
    Genera cilindros de control combinando:
    1. LA REJILLA (Cuadrados): Conexiones a distancia 'spacing'.
    2. LA DIAGONAL PARALELA: Conexiones a distancia diagonal PERO solo en dirección positiva.
    """
    if len(esferas) < 2: return []
    
    print(f" -> Generando Rejilla + Diagonales Paralelas (Gap: {gap_mm}mm)...")
    cilindros = []
    tree = KDTree(esferas)
    
    # Parámetros de distancias esperadas
    dist_grid = spacing_lattice                  # Lado del cuadrado
    dist_diag = spacing_lattice * np.sqrt(3)     # Diagonal del cubo
    
    # Tolerancia para errores de punto flotante
    tol = 0.5
    
    # Buscamos vecinos (k=27 escanea todo el cubo 3x3 alrededor)
    distancias, indices = tree.query(esferas, k=27) 
    
    pares_procesados = set()
    
    # Definimos el Vector Director Diagonal Unitario Aproximado (1, 1, 1)
    # Esto es para filtrar que las diagonales vayan todas al mismo lado
    vector_ref = np.array([1.0, 1.0, 1.0])
    vector_ref = vector_ref / np.linalg.norm(vector_ref)
    
    for i, lista_vecinos in enumerate(indices):
        p1 = esferas[i]
        
        for idx_vecino, dist in zip(lista_vecinos, distancias[i]):
            if i == idx_vecino: continue 
            
            p2 = esferas[idx_vecino]
            vector_real = p2 - p1
            norma_real = np.linalg.norm(vector_real)
            if norma_real == 0: continue
            
            unitario_real = vector_real / norma_real
            
            es_conector_valido = False
            
            # --- TIPO 1: CUADRADOS (GRID ORTOGONAL) ---
            if abs(dist - dist_grid) < tol:
                # Validamos que sea ortogonal puro (ejes X, Y o Z)
                # El producto punto con los ejes debe ser casi 1 o -1
                if (abs(unitario_real[0]) > 0.9 or abs(unitario_real[1]) > 0.9 or abs(unitario_real[2]) > 0.9):
                    es_conector_valido = True

            # --- TIPO 2: DIAGONAL (UNIDIRECCIONAL) ---
            elif abs(dist - dist_diag) < tol:
                # Calculamos el ángulo con nuestro vector referencia (1,1,1)
                # Producto punto cercano a 1 significa que van en la misma dirección
                cos_angulo = np.dot(unitario_real, vector_ref)
                
                # Si cos_angulo > 0.9, va en la dirección (1,1,1).
                # Si cos_angulo < -0.9, va en (-1,-1,-1) que es la misma línea hacia atrás.
                # Queremos evitar las otras diagonales cruzadas (ej: 1, -1, 1).
                if abs(cos_angulo) > 0.9:
                     es_conector_valido = True
            
            # --- AGREGAR SI ES VÁLIDO ---
            if es_conector_valido:
                # Evitar duplicados (p1-p2 es igual a p2-p1)
                idx_min, idx_max = sorted((i, idx_vecino))
                if (idx_min, idx_max) in pares_procesados: continue
                pares_procesados.add((idx_min, idx_max))
                
                # --- RECORTAR (GAP) ---
                recorte = radio_esfera + gap_mm
                if recorte * 2 < norma_real:
                    inicio = p1 + unitario_real * recorte
                    fin = p2 - unitario_real * recorte
                    cilindros.append((inicio, fin))

    return cilindros