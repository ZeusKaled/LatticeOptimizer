import numpy as np

def generar_grilla_candidatos(datos_img, paso_mm=3.0):
    """
    Genera una lista de coordenadas (x, y, z) dentro del GTV.
    No toma todos los píxeles, sino que da saltos ('paso_mm') para no saturar.
    
    Args:
        datos_img (dict): El diccionario que nos devuelve io_loader (mask, spacing, origin).
        paso_mm (float): Cada cuántos milímetros tomamos un punto.
    
    Returns:
        np.array: Una matriz de tamaño (N, 3) con las coordenadas físicas de los candidatos.
    """
    print(f"--- Generando grilla de candidatos (Paso: {paso_mm} mm) ---")
    
    mask = datos_img["array"]      # Matriz 3D (Z, Y, X)
    spacing = datos_img["spacing"] # (sx, sy, sz)
    origin = datos_img["origin"]   # (ox, oy, oz)
    
    # 1. Calcular el "salto" en índices de matriz
    # Si el píxel mide 1mm y queremos ir cada 3mm, saltamos de 3 en 3 índices.
    # max(1, ...) asegura que nunca sea 0.
    step_z = max(1, int(paso_mm / spacing[2]))
    step_y = max(1, int(paso_mm / spacing[1]))
    step_x = max(1, int(paso_mm / spacing[0]))
    
    candidatos = []
    
    # 2. Recorrer la matriz dando saltos (Optimización básica)
    # shape es (Z, Y, X) en NumPy
    z_len, y_len, x_len = mask.shape
    
    for k in range(0, z_len, step_z):
        for j in range(0, y_len, step_y):
            for i in range(0, x_len, step_x):
                
                # Si el vóxel vale 1 (es tumor)
                if mask[k, j, i] > 0:
                    
                    # 3. Convertir índice a Coordenada Física (Matemática médica)
                    # Posicion = Origen + (Indice * Tamaño_Voxel)
                    px = origin[0] + i * spacing[0]
                    py = origin[1] + j * spacing[1]
                    pz = origin[2] + k * spacing[2]
                    
                    candidatos.append([px, py, pz])
                    
    # Convertir a numpy array para cálculos rápidos después
    candidatos_np = np.array(candidatos)
    
    print(f" -> Puntos encontrados dentro del GTV: {len(candidatos_np)}")
    return candidatos_np