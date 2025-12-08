import cv2 as cv
import numpy as np

img = np.zeros((500, 500), np.uint8)

cv.circle(img, (200, 200), 60, (255), -1)
cv.rectangle(img, (80, 80), (180, 180), (255), -1)
cv.ellipse(img, (400, 400), (50, 70), 0, 0, 360, (255), -1)

cv.imshow("Figura Original", img)

primera_coord_x, primera_coord_y = None, None
for i in range(500):
    for j in range(500):
        if img[i, j] == 255:
            primera_coord_y, primera_coord_x = i, j
            break
    if primera_coord_x is not None:
        break

print(f"Primera coordenada: ({primera_coord_x}, {primera_coord_y})")

coordenadas_figura = []
for i in range(500):
    for j in range(500):
        if img[i, j] == 255:
            coordenadas_figura.append((j, i))

if coordenadas_figura:
    suma_x = sum(coord[0] for coord in coordenadas_figura)
    suma_y = sum(coord[1] for coord in coordenadas_figura)
    centroide_x = suma_x / len(coordenadas_figura)
    centroide_y = suma_y / len(coordenadas_figura)
    print(f"Centroide manual: ({centroide_x:.2f}, {centroide_y:.2f})")

contornos, _ = cv.findContours(img, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
img_resultado = cv.cvtColor(img, cv.COLOR_GRAY2BGR)

for i, contorno in enumerate(contornos):
    M = cv.moments(contorno)
    if M["m00"] != 0:
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
        print(f"Figura {i + 1} - Centroide con momentos: ({cx}, {cy})")
        cv.circle(img_resultado, (cx, cy), 8, (0, 0, 255), -1)
        cv.circle(img_resultado, (cx, cy), 3, (255, 255, 255), -1)

img_irregular = np.zeros((500, 500), np.uint8)
puntos = np.array([[80, 80], [350, 120], [180, 380]], np.int32)
cv.fillPoly(img_irregular, [puntos], 255)

contornos_irreg, _ = cv.findContours(img_irregular, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
img_irreg_resultado = cv.cvtColor(img_irregular, cv.COLOR_GRAY2BGR)

for contorno in contornos_irreg:
    M = cv.moments(contorno)
    if M["m00"] != 0:
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
        print(f"Centroide triángulo: ({cx}, {cy})")
        cv.circle(img_irreg_resultado, (cx, cy), 8, (0, 0, 255), -1)
        for punto in puntos:
            cv.circle(img_irreg_resultado, tuple(punto), 5, (0, 255, 0), -1)

cv.imshow("Figuras con Centroides", img_resultado)
cv.imshow("Triangulo Irregular", img_irreg_resultado)

cv.waitKey(0)
cv.destroyAllWindows()
