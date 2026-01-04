# Graficación - Portafolio de Proyectos

**Alumno:** Dueñas Cantero Axel Alberto  
**Número de Control:** 23121056  
**Profesor:** Jesús Eduardo Alcaraz Chávez  
**Material de Referencia:** [https://ealcaraz85.github.io/Graficacion.io/](https://ealcaraz85.github.io/Graficacion.io/)

---

## Introducción

Este repositorio contiene una colección de proyectos desarrollados en el marco de la materia de Graficación. Los trabajos abarcan desde técnicas básicas de procesamiento de imágenes hasta aplicaciones interactivas con visión por computadora, integrando librerías como OpenCV, MediaPipe y OpenGL. Cada proyecto tiene como objetivo demostrar la aplicación práctica de conceptos clave en el área, desde operadores puntuales hasta realidad aumentada y detección facial.

---

## Estructura del Repositorio

- [calculadora.py](#calculadora) – Calculadora interactiva controlada por gestos manuales.
- [invisibilidad.py](#invisibilidad) – Efecto de camuflaje mediante sustitución de fondo.
- [deteccion.py](#deteccion) – Detector de rostros con animaciones gráficas.
- [centroide.py](#centroide) – Cálculo de centroides en figuras geométricas.
- [centroide2.py](#centroide2) – Cálculo manual de centroides sin uso de contornos.
- [centroide_sin_contorno.py](#centroide_sin_contorno) – Cálculo de centroides globales por conectividad.
- [agrandar_cuadrado.py](#agrandar_cuadrado) – Control de tamaño de un cuadrado mediante distancia entre pulgares.
- [distancia.py](#distancia) – Similar al anterior, con medición de distancia en tiempo real.
- [manos.py](#manos) – Detección y seguimiento de manos con MediaPipe.
- [figura.py](#figura) – Creación de una figura de astronauta usando primitivas gráficas.
- [operador_puntual.py](#operador_puntual) – Aplicación de un operador puntual de umbralización.
- [rotacion.py](#rotacion) – Rotación manual de una imagen usando transformaciones geométricas.
- [split_merge.py](#split_merge) – Separación y recombinación de canales de color.
- [video.py](#video) – Procesamiento de video en tiempo real con división de canales.
- [Introduccion.py](#introduccion) – Introducción a OpenGL con GLFW, dibujo de primitivas.
- [piramide.py](#piramide) – Pirámide 3D en rotación continua con OpenGL.
- [parametricas.py](#parametricas) – Animación de una curva paramétrica
- [pixel_art.py](#pixel_art) – Generación de un robot estilo pixel art.
- [pong.py](#pong) – Implementación básica del juego Pong con OpenCV.
- [varita_magica.py](#varita_magica) – Sistema de pintura virtual controlado por color.
- [varita_magica_2.py](#varita_magica_2) – Versión extendida con múltiples colores y figuras.
- [deteccion_rostro.py](#deteccion_rostro) – Filtro de máscara facial 3D con MediaPipe.
- [filto.py](#filto) – Primer prototipo de filtro tipo Snapchat con animaciones básicas.
- [filto2.py](#filto2) – Versión mejorada del filtro, con más elementos y estabilidad.

---

## Descripción Detallada de Proyectos

### calculadora.py
Calculadora interactiva que utiliza la cámara y la librería MediaPipe para detectar gestos de las manos. Los dedos índices permiten seleccionar botones virtuales mostrados en pantalla, realizando operaciones aritméticas básicas tras una breve pausa sobre cada botón.

### invisibilidad.py
Implementa el efecto de "capa de invisibilidad" mediante sustitución de fondo. Detecta objetos verdes en tiempo real y los reemplaza con un fondo previamente capturado, simulando transparencia.

### deteccion.py
Detector de rostros con animaciones gráficas superpuestas. Utiliza Haar Cascades para la detección facial y dibuja elementos animados

### centroide.py, centroide2.py, centroide_sin_contorno.py
Tres enfoques para el cálculo de centroides en figuras geométricas:
- **centroide.py**: Uso de momentos de contornos con OpenCV.
- **centroide2.py**: Cálculo manual iterando sobre píxeles.
- **centroide_sin_contorno.py**: Método por conectividad y sin uso de contornos, separando figuras mediante inundación (flood fill).

### agrandar_cuadrado.py y distancia.py
Proyectos que utilizan MediaPipe Hands para medir la distancia entre los pulgares de ambas manos y ajustar proporcionalmente el tamaño de un cuadrado en pantalla. `distancia.py` es una variación que enfatiza la medición y visualización de la distancia.

### manos.py
Detección básica de manos y dibujo de landmarks y conexiones en tiempo real. Sirve como base para proyectos de interacción gestual.

### figura.py
Creación de una figura de astronauta utilizando únicamente primitivas gráficas de OpenCV (rectángulos, círculos, polígonos). Demuestra composición de imágenes mediante formas básicas.

### operador_puntual.py
Aplicación de un operador de umbralización para binarizar una imagen. Convierte píxeles por encima de un valor en blanco y el resto en negro.

### rotacion.py
Rotación manual de una imagen aplicando transformaciones geométricas sin usar funciones predefinidas de OpenCV. Implementa la matriz de rotación con senos y cosenos.

### split_merge.py
Manipulación de canales de color: separación de canales RGB y recombinación en diferentes órdenes para crear efectos cromáticos.

### video.py
Captura de video en tiempo real y procesamiento frame a frame, aplicando división de canales y recombinación para mostrar variaciones de color.

### Introduccion.py y piramide.py
Introducción a OpenGL mediante GLFW:
- **Introduccion.py**: Dibujo de primitivas 2D (cuadrados, triángulos) con transformaciones básicas.
- **piramide.py**: Creación de una pirámide 3D con rotación continua, manejo de profundidad y proyección en perspectiva.

### parametricas.py
Animación de una curva paramétrica (Limacon) que se dibuja progresivamente en pantalla, ilustrando el concepto de ecuaciones paramétricas en gráficos.

### pixel_art.py
Generación de un robot en estilo pixel art usando una matriz de píxeles y ampliación con interpolación nearest-neighbor para mantener los bordes definidos.

### pong.py
Implementación básica del clásico juego Pong con OpenCV, mostrando el movimiento y rebote de una pelota en un canvas.

### varita_magica.py y varita_magica_2.py
Sistema de pintura virtual controlado por detección de color:
- **varita_magica.py**: Permite dibujo libre y colocación de figuras básicas (círculos, rectángulos, líneas) con un objeto naranja.
- **varita_magica_2.py**: **Iteración y mejora** que agrega detección de múltiples colores, permitiendo cambiar el color del trazo dinámicamente y ampliando las opciones de figuras.

### deteccion_rostro.py
Filtro de realidad aumentada que superpone una máscara facial 3D animada sobre el rostro detectado, usando MediaPipe Face Mesh y OpenGL para renderizado.

### filto.py y filto2.py
Filtros tipo Snapchat con animaciones y elementos robóticos:
- **filto.py**: Prototipo inicial con máscara facial gris, antena animada y barra de ojos que cambia de color.
- **filto2.py**: **Iteración y mejora significativa** que incluye un rostro robótico más detallado, cejas, boca con visualizador de ondas (equalizer), mejor iluminación y estabilidad en la detección. Además, se añaden elementos como tornillos decorativos y un sistema de parpadeo más natural.

---

## Requisitos e Instalación

Para ejecutar los proyectos, se recomienda un entorno con Python 3.8 o superior y las siguientes librerías:
opencv-python
mediapipe
numpy
glfw
PyOpenGL

text

Puedes instalar las dependencias con:

```bash
pip install -r requirements.txt 

Este repositorio documenta el aprendizaje y aplicación de técnicas de graficación y visión computacional a lo largo del curso. Los proyectos abarcan desde fundamentos hasta aplicaciones interactivas, mostrando el uso de herramientas modernas como MediaPipe y OpenGL. Cada archivo es autocontenido y puede ejecutarse de manera independiente, sirviendo como referencia para futuros desarrollos en el área.
