import cv2 as cv
import numpy as np

def calcular_centroide_manual(imagen):
    contornos, _ = cv.findContours(imagen, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    centroides = []
    
    for i, contorno in enumerate(contornos):
        mascara = np.zeros_like(imagen)
        cv.drawContours(mascara, [contorno], -1, 255, -1)
        
        coordenadas_figura = []
        
        for fila in range(imagen.shape[0]):
            for columna in range(imagen.shape[1]):
                if mascara[fila, columna] == 255:
                    coordenadas_figura.append((columna, fila))
        
        if coordenadas_figura:
            suma_x = 0
            for coord in coordenadas_figura:
                suma_x += coord[0]
            
            suma_y = 0
            for coord in coordenadas_figura:
                suma_y += coord[1]
            
            centroide_x = suma_x / len(coordenadas_figura)
            centroide_y = suma_y / len(coordenadas_figura)
            
            centroides.append((int(centroide_x), int(centroide_y)))
    
    return centroides

canvas = np.zeros((600, 800), np.uint8)

cv.circle(canvas, (180, 180), 70, 255, -1)
cv.rectangle(canvas, (320, 120), (470, 220), 255, -1)
puntos_triangulo = np.array([[550, 120], [680, 220], [580, 280]], np.int32)
cv.fillPoly(canvas, [puntos_triangulo], 255)
cv.ellipse(canvas, (180, 380), (90, 50), 0, 0, 360, 255, -1)
puntos_irregular = np.array([
    [380, 320],
    [450, 300],
    [500, 340],
    [490, 400],
    [420, 420],
    [360, 390],
    [340, 360]
], np.int32)
cv.fillPoly(canvas, [puntos_irregular], 255)
cv.rectangle(canvas, (580, 380), (610, 480), 255, -1)
cv.rectangle(canvas, (610, 450), (680, 480), 255, -1)

cv.imshow("Figuras Originales", canvas)

centroides = calcular_centroide_manual(canvas)

canvas_resultado = cv.cvtColor(canvas, cv.COLOR_GRAY2BGR)

for i, (cx, cy) in enumerate(centroides):
    cv.circle(canvas_resultado, (cx, cy), 8, (0, 0, 255), -1)
    cv.circle(canvas_resultado, (cx, cy), 3, (255, 255, 255), -1)

cv.imshow("Centroides Calculados Manualmente", canvas_resultado)

cv.waitKey(0)
cv.destroyAllWindows()
