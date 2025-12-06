## README.md

# Proyecto: Máscara 3D con MediaPipe

## Descripción
Implementación de una máscara facial 3D en tiempo real utilizando OpenGL y MediaPipe. El sistema captura video de la cámara web, detecta rostros y superpone una máscara 3D que sigue los movimientos faciales.

## Cambios Principales Implementados

### 1. Tamaño de Ventana
- **Original:** 640×480 píxeles
- **Actual:** 1280×720 píxeles
- **Objetivo:** Mejorar la visibilidad y experiencia de visualización

### 2. Escala de la Máscara
- **Factor de escala general:** 2.5x (SCALE_FACTOR)
- **Factor de ensanchamiento:** 1.5x (WIDTH_SCALE)
- **Objetivo:** Rostro más ancho y proporciones mejoradas

### 3. Ajustes de Proporciones
- **Ojos:** Reposicionados 0.04 unidades hacia abajo
- **Cejas:** Ajustadas para mantener relación natural con los ojos
- **Objetivo:** Posicionamiento más natural de los rasgos faciales

### 4. Mejoras Técnicas
- Calidad de renderizado aumentada (20 segmentos en esferas)
- Iluminación optimizada para mejor contraste
- Configuración de MediaPipe ajustada para mayor precisión

## Requisitos de Instalación
```bash
pip install opencv-python mediapipe PyOpenGL glfw numpy
```

## Ejecución
```bash
python proyecto_final.py
```

## Instrucciones de Uso
1. Ejecutar el script
2. Permitir acceso a la cámara web
3. La máscara 3D se superpondrá automáticamente sobre el rostro detectado
4. Presionar ESC para salir

## Notas Técnicas
- La aplicación utiliza detección facial en tiempo real mediante MediaPipe
- Renderizado 3D implementado con OpenGL (fixed-function pipeline)
- El sistema sigue los movimientos faciales básicos
- Los parámetros de escala pueden ajustarse en las constantes del código

## Limitaciones
- Diseñado para un solo rostro a la vez
- Requiere iluminación adecuada para mejor detección
- El seguimiento funciona mejor con movimientos faciales moderados

## Estructura del Código
- `init_glfw()`: Inicialización de la ventana GLFW
- `setup_opengl()`: Configuración de OpenGL
- `render_3d_mask_extended()`: Renderizado principal de la máscara 3D
- `norm_landmark()`: Normalización de puntos faciales
- Funciones de dibujo para cada componente facial

Los cambios han mejorado significativamente la visibilidad y proporciones de la máscara facial, manteniendo la funcionalidad de seguimiento en tiempo real.
