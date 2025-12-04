import numpy as np
import math

def distancia_euclidiana(p1, p2):
    """Calcula distancia en mm entre dos puntos (x,y,z)."""
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2 + (p1[2]-p2[2])**2)

def optimizador_greedy(candidatos, num_esferas=5, distancia_min_mm=20.0):
    """
    Selecciona puntos usando una estrategia Voraz (Greedy):
    1. Empieza por el punto más cercano al centro del tumor.
    2. Busca el siguiente punto que esté al menos a 'distancia_min_mm' de los ya elegidos.
    3. Repite hasta alcanzar 'num_esferas' o quedarse sin espacio.
    
    Args:
        candidatos (np.array): Matriz (N, 3) con los puntos del grid.
        num_esferas (int): Cuántos vértices Lattice queremos conseguir.
        distancia_min_mm (float): Separación mínima centro-a-centro (ej. 60mm en Lattice clásico, 20mm para prueba).
        
    Returns:
        list: Lista de coordenadas [ [x,y,z], ... ] de las esferas seleccionadas.
    """
    print(f"--- Iniciando Optimización Greedy ---")
    print(f" -> Meta: {num_esferas} esferas | Separación min: {distancia_min_mm} mm")
    
    if len(candidatos) == 0:
        print("[ERROR] No hay candidatos.")
        return []

    # 1. Calcular el Centro de Masas (promedio de todos los puntos)
    centro_gtv = np.mean(candidatos, axis=0)
    
    # 2. Encontrar el candidato más cercano al centro para empezar (Estrategia Centro-Periferia)
    distancias_al_centro = np.linalg.norm(candidatos - centro_gtv, axis=1)
    indice_inicial = np.argmin(distancias_al_centro)
    
    elegidos = [candidatos[indice_inicial]]
    indices_elegidos = [indice_inicial]
    
    print(f" -> 1ª Esfera colocada en el centro: {np.round(elegidos[0], 2)}")
    
    # 3. Bucle para buscar el resto
    for i in range(num_esferas - 1):
        mejor_candidato = None
        
        # Recorremos todos los candidatos
        # (Nota: Esto se puede optimizar, pero para <5000 puntos es instantáneo)
        for idx, punto in enumerate(candidatos):
            if idx in indices_elegidos:
                continue # Ya lo usamos
            
            # Verificar si cumple la distancia con TODOS los ya elegidos
            es_valido = True
            for elegido in elegidos:
                d = distancia_euclidiana(punto, elegido)
                if d < distancia_min_mm:
                    es_valido = False
                    break
            
            if es_valido:
                # En la estrategia Greedy simple, tomamos el PRIMERO que encontremos válido
                # (O podríamos buscar el que esté más lejos, pero empecemos simple)
                mejor_candidato = punto
                indices_elegidos.append(idx)
                break 
        
        if mejor_candidato is not None:
            elegidos.append(mejor_candidato)
        else:
            print(f"[AVISO] No caben más esferas respetando la distancia. Se detuvo en {len(elegidos)}.")
            break
            
    # Convertir a numpy array para devolverlo limpio
    resultado = np.array(elegidos)
    print(f" -> Optimización finalizada. Esferas colocadas: {len(resultado)}")
    return resultado