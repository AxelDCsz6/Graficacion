import cv2 as cv

class DetectorRostroAnimado:
    def __init__(self):
        self.clasificador_facial = cv.CascadeClassifier(
            'modelos/haarcascade_frontalface_alt.xml'
        )
        self.capturador_video = cv.VideoCapture(0)
        
        # Variables para animaciones
        self.desplazamiento_ocular = 0
        self.direccion_movimiento_ojos = 1
        self.extension_lengua = 0
        self.direccion_movimiento_lengua = 1
        
    def procesar_cuadro_video(self, cuadro):
        escala_grises = cv.cvtColor(cuadro, cv.COLOR_BGR2GRAY)
        rostros_detectados = self.clasificador_facial.detectMultiScale(escala_grises, 1.3, 5)
        
        for (x, y, ancho, alto) in rostros_detectados:
            # Cálculo de proporciones faciales
            ancho_nasal = ancho // 5
            alto_nasal = alto // 3
            
            # Configuración ocular
            radio_contorno_ojo = int(ancho * 0.08)
            radio_globo_ocular = int(ancho * 0.075)
            radio_pupila = int(ancho * 0.025)
            limite_movimiento_ocular = radio_globo_ocular - radio_pupila
            
            # Configuración bucal
            posicion_y_boca = y + int(alto * 0.79)
            inicio_lengua = y + int(alto * 0.85)
            extension_maxima_lengua = int(alto * 0.12)
            
            # Posicionamiento orejas
            centro_oreja_izquierda = (x + int(ancho * 0.05), y + int(alto * 0.5))
            centro_oreja_derecha = (x + int(ancho * 0.95), y + int(alto * 0.5))
            
            # Elementos de sombrero
            limite_inferior_sombrero = y - int(alto * 0.15)
            limite_superior_sombrero = y - int(alto * 0.6)
            
            # Renderizar elementos faciales
            self._dibujar_sombrero(cuadro, x, y, ancho, alto, 
                                 limite_superior_sombrero, limite_inferior_sombrero)
            self._dibujar_estructura_facial(cuadro, x, y, ancho, alto)
            self._dibujar_organos_auditivos(cuadro, centro_oreja_izquierda, 
                                          centro_oreja_derecha, ancho, alto)
            self._dibujar_organos_visuales(cuadro, x, y, ancho, alto, 
                                         radio_contorno_ojo, radio_globo_ocular, 
                                         radio_pupila, limite_movimiento_ocular)
            self._dibujar_organo_nasal(cuadro, x, y, ancho_nasal, alto_nasal)
            self._dibujar_organo_bucal(cuadro, x, y, ancho, alto, ancho_nasal, 
                                     posicion_y_boca, inicio_lengua, extension_maxima_lengua)
                              
        return cuadro
        
    def _dibujar_sombrero(self, cuadro, x, y, ancho, alto, y_superior, y_inferior):
        # Cuerpo principal del sombrero
        cv.rectangle(cuadro, (x + int(ancho * 0.2), y_superior), 
                    (x + int(ancho * 0.8), y_inferior), (0, 0, 0), -1)
        # Ala del sombrero
        cv.rectangle(cuadro, (x - int(ancho * 0.1), y_inferior), 
                    (x + int(ancho * 1.1), y_inferior - int(alto * 0.05)), (0, 0, 0), -1)
        # Decoración del sombrero
        cv.rectangle(cuadro, (x + int(ancho * 0.2), y_inferior - int(alto * 0.1)), 
                    (x + int(ancho * 0.8), y_inferior - int(alto * 0.05)), (10, 0, 255), -1)
                    
    def _dibujar_estructura_facial(self, cuadro, x, y, ancho, alto):
        # Contorno facial azul
        cv.rectangle(cuadro, (x, y), (x + ancho, y + alto), (234, 23, 23), 5)
        # Área facial verde
        cv.rectangle(cuadro, (x, int(y + alto / 2)), (x + ancho, y + alto), (0, 255, 0), 5)
        
    def _dibujar_organos_auditivos(self, cuadro, centro_izq, centro_der, ancho, alto):
        cv.ellipse(cuadro, centro_izq, (int(ancho * 0.1), int(alto * 0.15)), 
                  0, 0, 360, (80, 222, 249), 2)
        cv.ellipse(cuadro, centro_der, (int(ancho * 0.1), int(alto * 0.15)), 
                  0, 0, 360, (80, 222, 249), 2)
                  
    def _dibujar_organos_visuales(self, cuadro, x, y, ancho, alto, radio_borde, 
                                radio_globo, radio_pupila, limite_movimiento):
        # Contorno ocular
        cv.circle(cuadro, (x + int(ancho * 0.3), y + int(alto * 0.4)), 
                 radio_borde, (0, 0, 0), 2)
        cv.circle(cuadro, (x + int(ancho * 0.7), y + int(alto * 0.4)), 
                 radio_borde, (0, 0, 0), 2)
        
        # Globos oculares
        cv.circle(cuadro, (x + int(ancho * 0.3), y + int(alto * 0.4)), 
                 radio_globo, (255, 255, 255), -1)
        cv.circle(cuadro, (x + int(ancho * 0.7), y + int(alto * 0.4)), 
                 radio_globo, (255, 255, 255), -1)
        
        # Pupilas con movimiento
        cv.circle(cuadro, (x + int(ancho * 0.3) + self.desplazamiento_ocular, 
                 y + int(alto * 0.4)), radio_pupila, (0, 0, 255), -1)
        cv.circle(cuadro, (x + int(ancho * 0.7) + self.desplazamiento_ocular, 
                 y + int(alto * 0.4)), radio_pupila, (0, 0, 255), -1)
        
        # Actualizar movimiento ocular
        if self.direccion_movimiento_ojos > 0:
            self.desplazamiento_ocular += 1
            if self.desplazamiento_ocular > limite_movimiento:
                self.direccion_movimiento_ojos *= -1
        else:
            self.desplazamiento_ocular -= 1
            if self.desplazamiento_ocular < -limite_movimiento:
                self.direccion_movimiento_ojos *= -1
                
    def _dibujar_organo_nasal(self, cuadro, x, y, ancho_nasal, alto_nasal):
        cv.rectangle(cuadro, (x + 2 * ancho_nasal, y + alto_nasal), 
                    (x + ancho_nasal * 3, y + alto_nasal * 2), (255, 0, 255), 2)
                    
    def _dibujar_organo_bucal(self, cuadro, x, y, ancho, alto, ancho_nasal, 
                            y_boca, inicio_lengua, max_extension):
        # Cavidad bucal
        cv.circle(cuadro, (x + int(2.5 * ancho_nasal), y_boca), 
                 int(ancho * 0.10), (10, 10, 10), -1)
                 
        # Lengua con movimiento
        cv.rectangle(cuadro, (x + int(2.25 * ancho_nasal), y_boca), 
                    (x + int(2.75 * ancho_nasal), inicio_lengua + self.extension_lengua), 
                    (0, 0, 255), -1)
                    
        # Actualizar movimiento lingual
        if self.direccion_movimiento_lengua > 0:
            self.extension_lengua += 2
            if self.extension_lengua > max_extension:
                self.direccion_movimiento_lengua *= -1
        else:
            self.extension_lengua -= 2
            if self.extension_lengua < 0:
                self.direccion_movimiento_lengua *= -1
                
    def ejecutar_deteccion(self):
        print("Detector Facial Animado activado")
        print("Presiona ESC para finalizar")
        
        while True:
            exito, cuadro = self.capturador_video.read()
            if not exito:
                break
                
            cuadro_procesado = self.procesar_cuadro_video(cuadro)
            cv.imshow('Detección Facial con Animaciones', cuadro_procesado)
            
            if cv.waitKey(2) & 0xFF == 27:
                break
                
        self.capturador_video.release()
        cv.destroyAllWindows()

def main():
    detector_principal = DetectorRostroAnimado()
    detector_principal.ejecutar_deteccion()

if __name__ == "__main__":
    main()
