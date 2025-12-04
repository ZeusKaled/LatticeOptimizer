import pyvista as pv
import numpy as np

def visualizar_lattice(candidatos, esferas, radio_esfera=3.0):
    """
    Genera una visualización 3D interactiva.
    
    Args:
        candidatos (np.array): Todos los puntos posibles (dibujará el GTV como una nube fantasma).
        esferas (np.array): Las coordenadas (x,y,z) seleccionadas por el optimizador.
        radio_esfera (float): Radio visual de las esferas Lattice (en mm).
    """
    print("--- Iniciando visualización 3D con PyVista ---")
    
    # 1. Crear el escenario (Plotter)
    p = pv.Plotter()
    p.set_background("black") # Fondo negro estilo radioterapia
    
    # 2. Dibujar el "Fantasma" del GTV (Nube de puntos)
    # Convertimos los puntos a una nube PyVista
    if len(candidatos) > 0:
        nube_gtv = pv.PolyData(candidatos)
        # Los pintamos como puntitos grises translúcidos
        p.add_mesh(nube_gtv, color="white", opacity=0.1, point_size=2, render_points_as_spheres=True, label="GTV (Nube)")

    # 3. Dibujar las Esferas Lattice (Vértices)
    for i, centro in enumerate(esferas):
        # Crear una esfera geométrica en esa coordenada
        esfera_geo = pv.Sphere(radius=radio_esfera, center=centro)
        
        # Añadir al escenario (Color Rojo Lattice)
        p.add_mesh(esfera_geo, color="red", opacity=0.9, smooth_shading=True)

    # 4. Añadir ejes y leyenda
    p.add_axes()
    p.add_text("Lattice Optimizer - Vista Previa", position='upper_left', font_size=10)
    
    print(" -> Abriendo ventana 3D... (Interactúa con el mouse)")
    p.show()