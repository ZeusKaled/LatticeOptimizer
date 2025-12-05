import pyvista as pv
import numpy as np

def visualizar_lattice_control(esferas, cilindros_control, radio_esfera=3.0, radio_cilindro=1.5):
    print("--- Visualización: Rojo=Target | Verde=Control de Dosis (Valle) ---")
    
    p = pv.Plotter()
    p.set_background("black")

    # 1. ESFERAS (Target)
    if len(esferas) > 0:
        nube = pv.PolyData(esferas)
        # Agregamos orient=False para evitar el Warning de PyVista
        glyphs = nube.glyph(scale=False, geom=pv.Sphere(radius=radio_esfera), orient=False)
        p.add_mesh(glyphs, color="red", opacity=1.0, label="GTV_Lattice (High Dose)")

    # 2. CILINDROS (Control/Avoidance)
    if len(cilindros_control) > 0:
        print(f" -> Renderizando {len(cilindros_control)} cilindros de control...")
        bloque_cilindros = pv.MultiBlock()
        
        for p1, p2 in cilindros_control:
            linea = pv.Line(p1, p2)
            tubo = linea.tube(radius=radio_cilindro)
            bloque_cilindros.append(tubo)
            
        p.add_mesh(bloque_cilindros, color="springgreen", opacity=0.5, label="Valley_Control")

    p.add_axes()
    p.add_legend()
    p.show()