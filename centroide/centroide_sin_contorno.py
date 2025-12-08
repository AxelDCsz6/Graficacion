import cv2 as cv
import numpy as np

def calcular_centroide_global_manual(imagen):
    todas_las_coordenadas = []
    
    for fila in range(imagen.shape[0]):
        for columna in range(imagen.shape[1]):
            if imagen[fila, columna] == 255:
                todas_las_coordenadas.append((columna, fila))
    
    if not todas_las_coordenadas:
        return None
    
    suma_x = 0
    suma_y = 0
    
    for x, y in todas_las_coordenadas:
        suma_x += x
        suma_y += y
    
    centroide_x = suma_x / len(todas_las_coordenadas)
    centroide_y = suma_y / len(todas_las_coordenadas)
    
    print(f"Centroide global: ({centroide_x:.2f}, {centroide_y:.2f})")
    
    return (int(centroide_x), int(centroide_y))

def separar_figuras_por_conectividad(imagen):
    imagen_trabajo = imagen.copy()
    figuras_separadas = []
    numero_figura = 1
    
    for fila in range(imagen.shape[0]):
        for columna in range(imagen.shape[1]):
            if imagen_trabajo[fila, columna] == 255:
                mascara = np.zeros((imagen.shape[0] + 2, imagen.shape[1] + 2), np.uint8)
                cv.floodFill(imagen_trabajo, mascara, (columna, fila), 128)
                
                coordenadas_figura = []
                for f in range(imagen.shape[0]):
                    for c in range(imagen.shape[1]):
                        if imagen_trabajo[f, c] == 128:
                            coordenadas_figura.append((c, f))
                
                if coordenadas_figura:
                    suma_x = sum(coord[0] for coord in coordenadas_figura)
                    suma_y = sum(coord[1] for coord in coordenadas_figura)
                    centroide_x = suma_x / len(coordenadas_figura)
                    centroide_y = suma_y / len(coordenadas_figura)
                    
                    figuras_separadas.append({
                        "numero": numero_figura,
                        "coordenadas": coordenadas_figura,
                        "centroide": (int(centroide_x), int(centroide_y)),
                        "area": len(coordenadas_figura)
                    })
                
                numero_figura += 1
    
    return figuras_separadas

canvas = np.zeros((500, 600), np.uint8)

cv.circle(canvas, (120, 120), 50, 255, -1)
cv.rectangle(canvas, (220, 180), (320, 280), 255, -1)
puntos_triangulo = np.array([[420, 100], [520, 180], [440, 220]], np.int32)
cv.fillPoly(canvas, [puntos_triangulo], 255)
puntos_irregular = np.array([[140, 380], [190, 340], [260, 380], [230, 440], [160, 420]], np.int32)
cv.fillPoly(canvas, [puntos_irregular], 255)

cv.imshow("Figuras Originales", canvas)

centroide_global = calcular_centroide_global_manual(canvas)

canvas_global = cv.cvtColor(canvas, cv.COLOR_GRAY2BGR)

if centroide_global:
    cx_global, cy_global = centroide_global
    cv.circle(canvas_global, (cx_global, cy_global), 10, (0, 0, 255), -1)
    cv.circle(canvas_global, (cx_global, cy_global), 4, (255, 255, 255), -1)

cv.imshow("Centroide Global (Sin Contornos)", canvas_global)

figuras_por_conectividad = separar_figuras_por_conectividad(canvas)

canvas_conectividad = cv.cvtColor(canvas, cv.COLOR_GRAY2BGR)

colores_figuras = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)]

for i, figura in enumerate(figuras_por_conectividad):
    cx, cy = figura["centroide"]
    color = colores_figuras[i % len(colores_figuras)]
    cv.circle(canvas_conectividad, (cx, cy), 8, color, -1)
    cv.circle(canvas_conectividad, (cx, cy), 3, (255, 255, 255), -1)

cv.imshow("Centroides por Conectividad", canvas_conectividad)

cv.waitKey(0)
cv.destroyAllWindows()
