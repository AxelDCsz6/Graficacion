import glfw
import cv2
import mediapipe as mp
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
import math

# Configuración de ventana
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Filtro Snapchat: Robot Futurista"

# Factores de escala aumentados
SCALE_FACTOR = 3.0  # Mucho más grande
WIDTH_SCALE = 2.0   # Mucho más ancho

# Conexiones para el contorno facial
contorno_cara = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288,
                 397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136,
                 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109]

# Puntos para ojos
LEFT_EYE = [33, 133, 160, 144, 158, 153]
RIGHT_EYE = [362, 263, 385, 380, 387, 374]

# Puntos para cejas
LEFT_EYEBROW = [70, 63, 105, 66, 107]
RIGHT_EYEBROW = [336, 296, 334, 293, 300]

# Puntos para boca
MOUTH_OUTER = [61, 291, 13, 14]

class RobotFilter:
    def __init__(self):
        self.eye_color = 0.0
        self.eye_color_dir = 1
        self.antenna_angle = 0.0
        self.antenna_dir = 1
        self.light_timer = 0.0
        self.blink_timer = 0.0
        
    def update_animation(self, delta_time):
        # Animación de cambio de color en ojos
        self.eye_color += delta_time * 1.5 * self.eye_color_dir
        if self.eye_color >= 1.0:
            self.eye_color = 1.0
            self.eye_color_dir = -1
        elif self.eye_color <= 0.0:
            self.eye_color = 0.0
            self.eye_color_dir = 1
            
        # Animación de antena
        self.antenna_angle += delta_time * 80 * self.antenna_dir
        if abs(self.antenna_angle) > 15:
            self.antenna_dir *= -1
            
        # Timer para luces
        self.light_timer += delta_time
        
        # Animación de parpadeo automático
        self.blink_timer += delta_time * 3

def init_glfw():
    if not glfw.init():
        raise Exception("No se pudo inicializar GLFW")
    
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 2)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 1)
    glfw.window_hint(glfw.RESIZABLE, glfw.TRUE)
    
    window = glfw.create_window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, None, None)
    
    if not window:
        glfw.terminate()
        raise Exception("No se pudo crear la ventana GLFW")
    
    glfw.make_context_current(window)
    glfw.swap_interval(1)
    
    return window

def setup_opengl():
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_LINE_SMOOTH)
    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
    glPointSize(8.0)  # Más grande
    glLineWidth(4.0)  # Más grueso
    
def setup_lights():
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    
    # Luz principal frontal
    glLightfv(GL_LIGHT0, GL_POSITION, (0, 0, 5, 1))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (1.5, 1.5, 1.5, 1))
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.5, 0.5, 0.5, 1))

def create_video_texture():
    video_tex = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, video_tex)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    return video_tex

def draw_sphere(x, y, z, radius, color=(1, 1, 1)):
    glPushMatrix()
    glTranslatef(x * SCALE_FACTOR * WIDTH_SCALE, y * SCALE_FACTOR, z * SCALE_FACTOR)
    glColor3f(*color)
    quad = gluNewQuadric()
    gluQuadricNormals(quad, GLU_SMOOTH)
    gluSphere(quad, radius * SCALE_FACTOR, 24, 24)
    gluDeleteQuadric(quad)
    glPopMatrix()

def draw_cube(center_x, center_y, center_z, width, height, depth, color=(0.5, 0.5, 0.5)):
    """Dibuja un cubo sólido MUY SIMPLE y visible"""
    half_w = width / 2
    half_h = height / 2
    half_d = depth / 2
    
    # Coordenadas ajustadas para que sean visibles
    vertices = [
        (center_x - half_w, center_y - half_h, center_z - half_d),
        (center_x + half_w, center_y - half_h, center_z - half_d),
        (center_x + half_w, center_y + half_h, center_z - half_d),
        (center_x - half_w, center_y + half_h, center_z - half_d),
        (center_x - half_w, center_y - half_h, center_z + half_d),
        (center_x + half_w, center_y - half_h, center_z + half_d),
        (center_x + half_w, center_y + half_h, center_z + half_d),
        (center_x - half_w, center_y + half_h, center_z + half_d)
    ]
    
    # Aplicar escala
    for i in range(len(vertices)):
        vertices[i] = (
            vertices[i][0] * SCALE_FACTOR * WIDTH_SCALE,
            vertices[i][1] * SCALE_FACTOR,
            vertices[i][2] * SCALE_FACTOR
        )
    
    faces = [
        [0, 1, 2, 3],  # Frente
        [4, 5, 6, 7],  # Atrás
        [0, 1, 5, 4],  # Abajo
        [2, 3, 7, 6],  # Arriba
        [0, 3, 7, 4],  # Izquierda
        [1, 2, 6, 5]   # Derecha
    ]
    
    glColor3f(*color)
    glBegin(GL_QUADS)
    for face in faces:
        for vertex in face:
            glVertex3f(*vertices[vertex])
    glEnd()

def norm_landmark(p):
    # Normalización simple y directa
    return (p.x - 0.5, -(p.y - 0.5), p.z)

def render_video_background(frame_rgb, video_tex):
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)
    
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1, 0, 1)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glBindTexture(GL_TEXTURE_2D, video_tex)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, 
                 frame_rgb.shape[1], frame_rgb.shape[0],
                 0, GL_RGB, GL_UNSIGNED_BYTE, frame_rgb)
    
    glColor3f(1.0, 1.0, 1.0)
    
    glEnable(GL_TEXTURE_2D)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 1); glVertex2f(0, 0)
    glTexCoord2f(1, 1); glVertex2f(1, 0)
    glTexCoord2f(1, 0); glVertex2f(1, 1)
    glTexCoord2f(0, 0); glVertex2f(0, 1)
    glEnd()
    glDisable(GL_TEXTURE_2D)
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_robot_mask(face_landmarks):
    """Dibuja la máscara principal del robot (cara gris) - SIMPLIFICADA"""
    lm = face_landmarks.landmark
    
    # Usar puntos clave para definir la máscara
    left_side = lm[234]  # Sien izquierda
    right_side = lm[454]  # Sien derecha
    forehead = lm[10]  # Frente
    chin = lm[152]  # Barbilla
    
    # Convertir a coordenadas normalizadas
    left_x, left_y, left_z = norm_landmark(left_side)
    right_x, right_y, right_z = norm_landmark(right_side)
    forehead_x, forehead_y, forehead_z = norm_landmark(forehead)
    chin_x, chin_y, chin_z = norm_landmark(chin)
    
    # Calcular centro y dimensiones
    center_x = (left_x + right_x) / 2
    center_y = (forehead_y + chin_y) / 2
    center_z = (left_z + right_z) / 2 + 0.3  # Adelantado para que sea visible
    
    width = abs(right_x - left_x) * 2.0
    height = abs(forehead_y - chin_y) * 1.8
    depth = 0.2  # Grosor fijo
    
    # Dibujar cara principal (GRANDE y GRIS CLARO)
    draw_cube(center_x, center_y, center_z, 
              width, height, depth, 
              (0.8, 0.8, 0.8))  # Gris claro
    
    # Dibujar frente (parte superior)
    draw_cube(center_x, forehead_y + 0.05, center_z + 0.1,
              width * 0.9, 0.05, depth * 0.8,
              (0.6, 0.6, 0.6))  # Gris medio

def draw_robot_eyes_bar(face_landmarks, robot_filter):
    """Dibuja una barra de ojos MUY VISIBLE que cambia de color"""
    lm = face_landmarks.landmark
    
    # Puntos para los ojos (simplificado)
    left_eye = lm[33]  # Esquina exterior ojo izquierdo
    right_eye = lm[263]  # Esquina exterior ojo derecho
    left_brow = lm[70]  # Ceja izquierda
    right_brow = lm[300]  # Ceja derecha
    
    lx, ly, lz = norm_landmark(left_eye)
    rx, ry, rz = norm_landmark(right_eye)
    lbx, lby, lbz = norm_landmark(left_brow)
    rbx, rby, rbz = norm_landmark(right_brow)
    
    # Posición Y entre ojos y cejas
    bar_y = (ly + ry) / 2 * 0.3 + (lby + rby) / 2 * 0.7
    
    # Dibujar barra principal (MUY GRUESA Y VISIBLE)
    glDisable(GL_LIGHTING)
    
    # Color que cambia con la animación
    r = 0.0
    g = 0.8 + robot_filter.eye_color * 0.2
    b = 0.2
    
    glColor3f(r, g, b)
    glLineWidth(20.0)  # MUY GRUESO
    
    # Barra completa de ojo a ojo
    glBegin(GL_LINES)
    glVertex3f((lx - 0.05) * SCALE_FACTOR * WIDTH_SCALE,
               bar_y * SCALE_FACTOR,
               (lz + 0.5) * SCALE_FACTOR)  # Adelantado para ser visible
    glVertex3f((rx + 0.05) * SCALE_FACTOR * WIDTH_SCALE,
               bar_y * SCALE_FACTOR,
               (rz + 0.5) * SCALE_FACTOR)
    glEnd()
    
    # Puntos en los extremos (para destacar)
    glPointSize(30.0)
    glBegin(GL_POINTS)
    glVertex3f((lx - 0.05) * SCALE_FACTOR * WIDTH_SCALE,
               bar_y * SCALE_FACTOR,
               (lz + 0.5) * SCALE_FACTOR)
    glVertex3f((rx + 0.05) * SCALE_FACTOR * WIDTH_SCALE,
               bar_y * SCALE_FACTOR,
               (rz + 0.5) * SCALE_FACTOR)
    glEnd()
    
    glEnable(GL_LIGHTING)

def draw_robot_antenna(face_landmarks, robot_filter):
    """Dibuja una antena GRANDE y VISIBLE en la frente"""
    lm = face_landmarks.landmark
    forehead = lm[10]
    
    fx, fy, fz = norm_landmark(forehead)
    
    # Posición: en medio de la frente, ALTA
    glPushMatrix()
    glTranslatef(fx * SCALE_FACTOR * WIDTH_SCALE,
                 (fy + 0.25) * SCALE_FACTOR,  # MUY ARRIBA
                 (fz + 0.4) * SCALE_FACTOR)   # MUY ADELANTE
    
    # Añadir algo de movimiento
    glRotatef(math.sin(robot_filter.light_timer * 2) * 10, 0, 0, 1)
    
    # Antena principal (CONO GRANDE)
    glColor3f(0.9, 0.4, 0.1)  # NARANJA FUERTE
    
    quad = gluNewQuadric()
    
    # Base ancha
    gluCylinder(quad, 0.06 * SCALE_FACTOR, 0.04 * SCALE_FACTOR,
                0.3 * SCALE_FACTOR, 16, 2)
    
    # Sección media
    glTranslatef(0, 0, 0.3 * SCALE_FACTOR)
    gluCylinder(quad, 0.04 * SCALE_FACTOR, 0.02 * SCALE_FACTOR,
                0.2 * SCALE_FACTOR, 16, 2)
    
    # Punta
    glTranslatef(0, 0, 0.2 * SCALE_FACTOR)
    gluCylinder(quad, 0.02 * SCALE_FACTOR, 0.0,
                0.1 * SCALE_FACTOR, 16, 2)
    
    # Esfera brillante en la punta
    glPushMatrix()
    glTranslatef(0, 0, -0.05 * SCALE_FACTOR)
    glColor3f(1.0, 1.0, 0.5)  # Amarillo brillante
    gluSphere(quad, 0.04 * SCALE_FACTOR, 16, 16)
    
    # Luz parpadeante
    if math.sin(robot_filter.light_timer * 8) > 0:
        glColor3f(1.0, 1.0, 1.0)
        gluSphere(quad, 0.02 * SCALE_FACTOR, 12, 12)
    glPopMatrix()
    
    gluDeleteQuadric(quad)
    glPopMatrix()

def draw_robot_mouth(face_landmarks, robot_filter):
    """Dibuja una boca MUY VISIBLE"""
    lm = face_landmarks.landmark
    
    # Puntos de la boca
    mouth_left = lm[61]
    mouth_right = lm[291]
    mouth_top = lm[13]
    mouth_bottom = lm[14]
    
    mlx, mly, mlz = norm_landmark(mouth_left)
    mrx, mry, mrz = norm_landmark(mouth_right)
    mtx, mty, mtz = norm_landmark(mouth_top)
    mbx, mby, mbz = norm_landmark(mouth_bottom)
    
    # Centro de la boca
    center_x = (mlx + mrx) / 2
    center_y = (mty + mby) / 2
    center_z = (mlz + mrz) / 2 + 0.4  # MUY ADELANTADO
    
    # Tamaño basado en la boca real
    width = abs(mrx - mlx) * 1.5
    height = abs(mty - mby) * 1.2
    
    # Dibujar boca principal (ROJO FUERTE)
    glDisable(GL_LIGHTING)
    glColor3f(1.0, 0.2, 0.2)
    
    # Boca como rectángulo 3D simple
    glBegin(GL_QUADS)
    
    # Frente
    glVertex3f((center_x - width/2) * SCALE_FACTOR * WIDTH_SCALE,
               (center_y - height/4) * SCALE_FACTOR,
               center_z * SCALE_FACTOR)
    glVertex3f((center_x + width/2) * SCALE_FACTOR * WIDTH_SCALE,
               (center_y - height/4) * SCALE_FACTOR,
               center_z * SCALE_FACTOR)
    glVertex3f((center_x + width/2) * SCALE_FACTOR * WIDTH_SCALE,
               (center_y + height/4) * SCALE_FACTOR,
               center_z * SCALE_FACTOR)
    glVertex3f((center_x - width/2) * SCALE_FACTOR * WIDTH_SCALE,
               (center_y + height/4) * SCALE_FACTOR,
               center_z * SCALE_FACTOR)
    
    # Arriba
    glVertex3f((center_x - width/2) * SCALE_FACTOR * WIDTH_SCALE,
               (center_y + height/4) * SCALE_FACTOR,
               center_z * SCALE_FACTOR)
    glVertex3f((center_x + width/2) * SCALE_FACTOR * WIDTH_SCALE,
               (center_y + height/4) * SCALE_FACTOR,
               center_z * SCALE_FACTOR)
    glVertex3f((center_x + width/2) * SCALE_FACTOR * WIDTH_SCALE,
               (center_y + height/4) * SCALE_FACTOR,
               (center_z - 0.05) * SCALE_FACTOR)
    glVertex3f((center_x - width/2) * SCALE_FACTOR * WIDTH_SCALE,
               (center_y + height/4) * SCALE_FACTOR,
               (center_z - 0.05) * SCALE_FACTOR)
    
    # Abajo
    glVertex3f((center_x - width/2) * SCALE_FACTOR * WIDTH_SCALE,
               (center_y - height/4) * SCALE_FACTOR,
               center_z * SCALE_FACTOR)
    glVertex3f((center_x + width/2) * SCALE_FACTOR * WIDTH_SCALE,
               (center_y - height/4) * SCALE_FACTOR,
               center_z * SCALE_FACTOR)
    glVertex3f((center_x + width/2) * SCALE_FACTOR * WIDTH_SCALE,
               (center_y - height/4) * SCALE_FACTOR,
               (center_z - 0.05) * SCALE_FACTOR)
    glVertex3f((center_x - width/2) * SCALE_FACTOR * WIDTH_SCALE,
               (center_y - height/4) * SCALE_FACTOR,
               (center_z - 0.05) * SCALE_FACTOR)
    
    glEnd()
    
    # Línea central de la boca (NEGRA)
    glColor3f(0.0, 0.0, 0.0)
    glLineWidth(8.0)
    
    glBegin(GL_LINES)
    glVertex3f((center_x - width/3) * SCALE_FACTOR * WIDTH_SCALE,
               center_y * SCALE_FACTOR,
               (center_z + 0.01) * SCALE_FACTOR)
    glVertex3f((center_x + width/3) * SCALE_FACTOR * WIDTH_SCALE,
               center_y * SCALE_FACTOR,
               (center_z + 0.01) * SCALE_FACTOR)
    glEnd()
    
    glEnable(GL_LIGHTING)

def draw_robot_eyebrows(face_landmarks):
    """Dibuja cejas SIMPLES y VISIBLES"""
    lm = face_landmarks.landmark
    
    # Ceja izquierda
    left_points = [lm[i] for i in LEFT_EYEBROW]
    left_xs = [norm_landmark(p)[0] for p in left_points]
    left_ys = [norm_landmark(p)[1] for p in left_points]
    left_zs = [norm_landmark(p)[2] for p in left_points]
    
    left_center_x = sum(left_xs) / len(left_xs)
    left_center_y = sum(left_ys) / len(left_ys) - 0.02
    left_center_z = sum(left_zs) / len(left_zs) + 0.4  # Adelantado
    
    left_width = (max(left_xs) - min(left_xs)) * 1.5
    left_height = 0.05
    
    # Ceja derecha
    right_points = [lm[i] for i in RIGHT_EYEBROW]
    right_xs = [norm_landmark(p)[0] for p in right_points]
    right_ys = [norm_landmark(p)[1] for p in right_points]
    right_zs = [norm_landmark(p)[2] for p in right_points]
    
    right_center_x = sum(right_xs) / len(right_xs)
    right_center_y = sum(right_ys) / len(right_ys) - 0.02
    right_center_z = sum(right_zs) / len(right_zs) + 0.4  # Adelantado
    
    right_width = (max(right_xs) - min(right_xs)) * 1.5
    right_height = 0.05
    
    # Dibujar cejas (NEGRAS)
    glDisable(GL_LIGHTING)
    glColor3f(0.0, 0.0, 0.0)
    
    # Ceja izquierda (rectángulo simple)
    glBegin(GL_QUADS)
    glVertex3f((left_center_x - left_width/2) * SCALE_FACTOR * WIDTH_SCALE,
               (left_center_y - left_height/2) * SCALE_FACTOR,
               left_center_z * SCALE_FACTOR)
    glVertex3f((left_center_x + left_width/2) * SCALE_FACTOR * WIDTH_SCALE,
               (left_center_y - left_height/2) * SCALE_FACTOR,
               left_center_z * SCALE_FACTOR)
    glVertex3f((left_center_x + left_width/2) * SCALE_FACTOR * WIDTH_SCALE,
               (left_center_y + left_height/2) * SCALE_FACTOR,
               left_center_z * SCALE_FACTOR)
    glVertex3f((left_center_x - left_width/2) * SCALE_FACTOR * WIDTH_SCALE,
               (left_center_y + left_height/2) * SCALE_FACTOR,
               left_center_z * SCALE_FACTOR)
    glEnd()
    
    # Ceja derecha (rectángulo simple)
    glBegin(GL_QUADS)
    glVertex3f((right_center_x - right_width/2) * SCALE_FACTOR * WIDTH_SCALE,
               (right_center_y - right_height/2) * SCALE_FACTOR,
               right_center_z * SCALE_FACTOR)
    glVertex3f((right_center_x + right_width/2) * SCALE_FACTOR * WIDTH_SCALE,
               (right_center_y - right_height/2) * SCALE_FACTOR,
               right_center_z * SCALE_FACTOR)
    glVertex3f((right_center_x + right_width/2) * SCALE_FACTOR * WIDTH_SCALE,
               (right_center_y + right_height/2) * SCALE_FACTOR,
               right_center_z * SCALE_FACTOR)
    glVertex3f((right_center_x - right_width/2) * SCALE_FACTOR * WIDTH_SCALE,
               (right_center_y + right_height/2) * SCALE_FACTOR,
               right_center_z * SCALE_FACTOR)
    glEnd()
    
    glEnable(GL_LIGHTING)

def render_robot_filter(face_landmarks, robot_filter):
    """Renderiza el filtro completo de robot - SIMPLIFICADO"""
    glEnable(GL_DEPTH_TEST)
    glClear(GL_DEPTH_BUFFER_BIT)
    
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluPerspective(50, WINDOW_WIDTH/WINDOW_HEIGHT, 0.1, 100)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Mover la cámara un poco más cerca
    gluLookAt(0, 0, 2.0, 0, 0, 0, 0, 1, 0)
    
    setup_lights()
    
    # IMPORTANTE: Deshabilitar iluminación temporalmente para colores sólidos
    glDisable(GL_LIGHTING)
    
    # Dibujar en este orden (de atrás hacia adelante):
    # 1. Máscara gris
    draw_robot_mask(face_landmarks)
    
    # 2. Cejas
    draw_robot_eyebrows(face_landmarks)
    
    # 3. Barra de ojos
    draw_robot_eyes_bar(face_landmarks, robot_filter)
    
    # 4. Boca
    draw_robot_mouth(face_landmarks, robot_filter)
    
    # 5. Antena (última para que esté más adelante)
    draw_robot_antenna(face_landmarks, robot_filter)
    
    glEnable(GL_LIGHTING)
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def main():
    try:
        window = init_glfw()
    except Exception as e:
        print(f"Error al inicializar GLFW: {e}")
        return
    
    setup_opengl()
    video_tex = create_video_texture()
    
    # Inicializar MediaPipe Face Mesh
    mp_face = mp.solutions.face_mesh
    face_mesh = mp_face.FaceMesh(
        static_image_mode=False,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,  # Más bajo para mejor detección
        min_tracking_confidence=0.5
    )
    
    # Inicializar filtro de robot
    robot_filter = RobotFilter()
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("No se pudo abrir la cámara")
        glfw.terminate()
        return
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, WINDOW_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, WINDOW_HEIGHT)
    print(f"Cámara inicializada en {WINDOW_WIDTH}x{WINDOW_HEIGHT}")
    
    frame_count = 0
    fps_timer = glfw.get_time()
    last_time = glfw.get_time()
    
    try:
        while not glfw.window_should_close(window):
            ret, frame = cap.read()
            if not ret:
                break
            
            frame = cv2.flip(frame, 1)
            frame = cv2.resize(frame, (WINDOW_WIDTH, WINDOW_HEIGHT))
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            results = face_mesh.process(frame_rgb)
            
            glfw.poll_events()
            
            if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
                break
            
            # Calcular delta time para animaciones
            current_time = glfw.get_time()
            delta_time = current_time - last_time
            last_time = current_time
            
            # Actualizar animaciones
            robot_filter.update_animation(delta_time)
            
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            
            # Renderizar video de fondo
            render_video_background(frame_rgb, video_tex)
            
            # Renderizar filtro si se detecta cara
            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    render_robot_filter(face_landmarks, robot_filter)
            
            glfw.swap_buffers(window)
            
            # Actualizar FPS en título
            frame_count += 1
            if current_time - fps_timer >= 1.0:
                fps = frame_count / (current_time - fps_timer)
                glfw.set_window_title(window, f"{WINDOW_TITLE} - FPS: {fps:.1f}")
                frame_count = 0
                fps_timer = current_time
    
    except Exception as e:
        print(f"Error en el loop principal: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\nCerrando aplicación...")
        cap.release()
        face_mesh.close()
        glfw.terminate()

if __name__ == "__main__":
    main()
