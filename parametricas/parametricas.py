import cv2
import numpy as np

# Definir los parámetros iniciales
width, height = 1000, 1000
img = np.ones((height, width, 3), dtype=np.uint8) * 255

# Parámetros de la curva de Limacon
a, b = 150, 100
k = 0.7
theta_increment = 0.05
max_theta = 2 * np.pi

# Centro de la imagen
center_x, center_y = width // 2, height // 2

theta = 0

while True:
    for t in np.arange(0, theta, theta_increment):
        r = a + b * np.cos(k * t)
        x = int(center_x + r * np.cos(t))
        y = int(center_y + r * np.sin(t))

        cv2.circle(img, (x - 2, y - 2), 3, (0, 0, 0), -1)

    cv2.imshow("Parametric Animation", img)

    theta += theta_increment

    if cv2.waitKey(30) & 0xFF == 27:
        break

cv2.destroyAllWindows()

