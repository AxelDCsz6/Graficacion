import cv2
import numpy as np

def inicializar_camara():
    camara = cv2.VideoCapture(0)
    camara.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camara.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    camara.set(cv2.CAP_PROP_FPS, 30)
    return camara

def crear_mascara_verde(frame_hsv):
    verde_oscuro = np.array([35, 40, 40])
    verde_claro = np.array([85, 255, 255])
    
    mascara_base = cv2.inRange(frame_hsv, verde_oscuro, verde_claro)
    nucleo = np.ones((5, 5), np.uint8)
    mascara_mejorada = cv2.morphologyEx(mascara_base, cv2.MORPH_CLOSE, nucleo)
    mascara_mejorada = cv2.morphologyEx(mascara_mejorada, cv2.MORPH_OPEN, nucleo)
    
    return mascara_mejorada

def main():
    # Configuración inicial
    capturador = inicializar_camara()
    print("Configurando fondo de referencia...")
    cv2.waitKey(1000)
    
    exito, fondo_referencia = capturador.read()
    if not exito:
        print("Error al inicializar cámara")
        return

    print("Efecto de invisibilidad activado. Use objeto verde.")
    
    while capturador.isOpened():
        exito, cuadro_actual = capturador.read()
        if not exito:
            break

        espacio_hsv = cv2.cvtColor(cuadro_actual, cv2.COLOR_BGR2HSV)
        mascara_verde = crear_mascara_verde(espacio_hsv)
        mascara_invertida = cv2.bitwise_not(mascara_verde)

        area_visible = cv2.bitwise_and(cuadro_actual, cuadro_actual, mask=mascara_invertida)
        area_reemplazo = cv2.bitwise_and(fondo_referencia, fondo_referencia, mask=mascara_verde)
        composicion_final = cv2.add(area_visible, area_reemplazo)
        cv2.imshow("Efecto Camuflaje", composicion_final)
        cv2.imshow("Mascara de Deteccion", mascara_verde)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    capturador.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
