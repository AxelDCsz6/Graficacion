import cv2 as cv
import numpy as np

def crear_robot_pixel_art():
    alto, ancho = 40, 30
    lienzo = np.full((alto, ancho), 255, dtype=np.uint8)
    
    NEGRO, GRIS_OSCURO, GRIS_MEDIO, AZUL, BLANCO = 0, 80, 160, 200, 255

    cabeza = [
        (5, list(range(10, 20))),
        (6, list(range(9, 21))),
        (7, list(range(8, 22))),
        (8, list(range(8, 22))),
        (9, list(range(8, 22))),
        (10, list(range(8, 22))),
    ]
    
    antenas = [(3, 12), (3, 17), (4, 12), (4, 17)]
    
    ojos = [
        (7, [11, 12, 18, 19]),
        (8, [11, 12, 18, 19]),
        (9, [11, 12, 18, 19]),
    ]
    
    boca = [
        (11, list(range(12, 18))),
        (12, list(range(12, 18))),
    ]

    cuerpo = [
        (13, list(range(7, 23))),
        (14, list(range(6, 24))),
        (15, list(range(6, 24))),
        (16, list(range(6, 24))),
        (17, list(range(6, 24))),
        (18, list(range(6, 24))),
    ]

    brazo_izq = [(15, 4), (16, 4), (17, 4), (15, 5), (16, 5), (17, 5)]
    brazo_der = [(15, 24), (16, 24), (17, 24), (15, 25), (16, 25), (17, 25)]
    
    pierna_izq = [(19, 9), (20, 9), (21, 9), (22, 9), (19, 10), (20, 10), (21, 10), (22, 10)]
    pierna_der = [(19, 19), (20, 19), (21, 19), (22, 19), (19, 20), (20, 20), (21, 20), (22, 20)]

    for y, xs in cabeza:
        for x in xs:
            lienzo[y, x] = GRIS_MEDIO
    
    for y, x in antenas:
        lienzo[y, x] = NEGRO
        
    for y, xs in ojos:
        for x in xs:
            lienzo[y, x] = AZUL
            
    for y, xs in boca:
        for x in xs:
            lienzo[y, x] = BLANCO
            
    for y, xs in cuerpo:
        for x in xs:
            lienzo[y, x] = GRIS_OSCURO
            
    for y, x in brazo_izq + brazo_der:
        lienzo[y, x] = GRIS_MEDIO
        
    for y, x in pierna_izq + pierna_der:
        lienzo[y, x] = GRIS_OSCURO

    return lienzo

def visualizar_pixel_art(imagen, escala=15, titulo="Robot Pixel Art"):
    alto, ancho = imagen.shape
    imagen_ampliada = cv.resize(imagen, (ancho * escala, alto * escala), 
                              interpolation=cv.INTER_NEAREST)
    cv.imshow(titulo, imagen_ampliada)
    print(f"Pixel Art creado: {ancho}x{alto} píxeles")
    print("Colores utilizados:", np.unique(imagen))

def main():
    print("Generando Pixel Art...")
    robot = crear_robot_pixel_art()
    visualizar_pixel_art(robot)
    
    # Guardar imagen
    cv.imwrite("robot_pixel_art.png", cv.resize(robot, (300, 400), interpolation=cv.INTER_NEAREST))
    print("Imagen guardada")
    
    cv.waitKey(0)
    cv.destroyAllWindows()

if __name__ == "__main__":
    main()
