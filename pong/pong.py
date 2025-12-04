import cv2 as cv
import numpy as np

# Definir el canvas
img = np.ones((500, 500, 3), np.uint8) * 255  # Imagen inicial con 3 canales

pos_x, pos_y = 400, 400
vel_x, vel_y = 5, 5
radio = 5
while True:
    img[:] = 255
    cv.circle(img, (pos_x, pos_y), radio, (0, 0, 255), -1)

    pos_x += vel_x
    pos_y += vel_y

    if pos_x - radio <= 0 or pos_x + radio >= img.shape[1]:
        vel_x = -vel_x
    if pos_y - radio <= 0 or pos_y + radio >= img.shape[0]:
        vel_y = -vel_y
    cv.imshow('Pong', img)
    key = cv.waitKey(30)
    if key == 27:  # Esc para salir
        break
cv.destroyAllWindows()
