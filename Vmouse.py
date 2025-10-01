import os
import cv2
import mediapipe as mp
import pyautogui
import math
import numpy as np
import time
import sys
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QPropertyAnimation, QEasingCurve, QTimer, QRectF, QSize, QPointF
from PyQt6.QtGui import QAction, QImage, QPixmap, QIcon, QPainter, QColor, QLinearGradient, QFont
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QMessageBox, QFrame

# ------------------------
# Filtre de Kalman 1D (pour lisser le mouvement du curseur)
# ------------------------
class KalmanFilter1D:
    def __init__(self, process_noise=1e-3, measurement_noise=1e-2, estimation_error=1e-1):
        self.Q = process_noise
        self.R = measurement_noise
        self.P = estimation_error
        self.X = 0.0
        self.K = 0.0

    def update(self, measurement):
        self.P += self.Q
        self.K = self.P / (self.P + self.R)
        self.X = self.X + self.K * (measurement - self.X)
        self.P = (1 - self.K) * self.P
        return self.X

# ------------------------
# Initialisation MediaPipe Hands
# ------------------------
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
mp_draw = mp.solutions.drawing_utils

# ------------------------
# Taille de l'écran pour pyautogui
# ------------------------
screen_width, screen_height = pyautogui.size()

# ------------------------
# Paramètres pour lisser les mouvements
# ------------------------
lerp_min, lerp_max = 0.2, 0.6
dead_zone_min = 5

# ------------------------
# Filtres de Kalman sur X et Y
# ------------------------
kf_x, kf_y = KalmanFilter1D(), KalmanFilter1D()

# ------------------------
# États de tracking par main (suivi index)
# ------------------------
right_tracking = {'last_index_x': None, 'last_index_y': None}
left_tracking = {'last_index_x': None, 'last_index_y': None}

# ------------------------
# État pour mouvement curseur (seulement main droite)
# ------------------------
right_movement = {'last_screen_x': None, 'last_screen_y': None, 'last_index_x': None, 'last_index_y': None}

# ------------------------
# Webcam configuration (reduced resolution for smaller window)
# ------------------------
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
cap.set(cv2.CAP_PROP_FPS, 30)

# ------------------------
# Sensibilité non linéaire → rend le mouvement plus naturel
# ------------------------
def sensibilité_non_lin(delta, facteur_max=2.5):
    return np.sign(delta) * (abs(delta) ** 0.7) * facteur_max

# ------------------------
# Calcul de distance entre deux landmarks
# ------------------------
def calc_distance(lm1, lm2):
    return math.hypot(lm1.x - lm2.x, lm1.y - lm2.y)

# ------------------------
# Paramètres clic
# ------------------------
clic_en_cours = False
distance_pincement_min = 0.05
temps_dernier_clic = 0
delai_clic = 0.2
temps_pincement_min = 0.15
main_stable_threshold = 0.02
temps_debut_pincement = None

# ------------------------
# Paramètres scroll
# ------------------------
scroll_amount = 2.5
scroll_delay = 0.4
last_scroll_time = 0

# ------------------------
# Thread séparé pour gérer la vidéo et la détection
# ------------------------
class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()
        self.running = False

    def run(self):
        global running, right_movement, right_tracking, left_tracking
        global kf_x, kf_y, clic_en_cours, temps_dernier_clic, temps_debut_pincement, last_scroll_time

        while self.running:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = hands.process(rgb_frame)

            if result.multi_hand_landmarks:
                for hand_landmarks, hand_type in zip(result.multi_hand_landmarks, result.multi_handedness):
                    label = hand_type.classification[0].label
                    is_right = label == "Right"
                    poignet = hand_landmarks.landmark[0]
                    main_utilisable = poignet.y < 0.8

                    couleur_main = (0, 255, 0) if main_utilisable else (0, 0, 255)
                    mp_draw.draw_landmarks(
                        frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                        mp_draw.DrawingSpec(color=couleur_main, thickness=2, circle_radius=4),
                        mp_draw.DrawingSpec(color=couleur_main, thickness=2)
                    )

                    index_tip = hand_landmarks.landmark[8]
                    pouce_tip = hand_landmarks.landmark[4]
                    index_pip = hand_landmarks.landmark[6]
                    majeur_pip = hand_landmarks.landmark[10]
                    majeur_tip = hand_landmarks.landmark[12]
                    annulaire_pip = hand_landmarks.landmark[14]
                    auriculaire_pip = hand_landmarks.landmark[18]
                    index_base = hand_landmarks.landmark[5]

                    taille_main = calc_distance(poignet, index_base)
                    distance_seuil = taille_main * 0.6
                    dist_index_pouce = calc_distance(index_tip, pouce_tip)

                    tracking = right_tracking if is_right else left_tracking
                    main_stable = True
                    if tracking['last_index_x'] is not None:
                        deplacement = math.hypot(index_tip.x - tracking['last_index_x'], index_tip.y - tracking['last_index_y'])
                        main_stable = deplacement <= main_stable_threshold

                    index_levé = index_tip.y < index_pip.y
                    autres_pliés = (
                        hand_landmarks.landmark[12].y > majeur_pip.y and
                        hand_landmarks.landmark[16].y > annulaire_pip.y and
                        hand_landmarks.landmark[20].y > auriculaire_pip.y
                    )

                    if is_right and index_levé and autres_pliés and dist_index_pouce > distance_seuil and main_utilisable:
                        movement_state = right_movement
                        if movement_state['last_index_x'] is not None:
                            dx = index_tip.x - movement_state['last_index_x']
                            dy = index_tip.y - movement_state['last_index_y']
                            dx = sensibilité_non_lin(dx) * screen_width
                            dy = sensibilité_non_lin(dy) * screen_height
                            target_x = movement_state['last_screen_x'] + dx
                            target_y = movement_state['last_screen_y'] + dy
                        else:
                            target_x = index_tip.x * screen_width
                            target_y = index_tip.y * screen_height

                        smooth_x = kf_x.update(target_x)
                        smooth_y = kf_y.update(target_y)

                        vitesse = math.hypot(index_tip.x - movement_state['last_index_x'], index_tip.y - movement_state['last_index_y']) if movement_state['last_index_x'] is not None else 0
                        lerp_factor = np.clip(lerp_max - vitesse * 2, lerp_min, lerp_max)

                        if movement_state['last_screen_x'] is None:
                            movement_state['last_screen_x'], movement_state['last_screen_y'] = smooth_x, smooth_y

                        cursor_x = movement_state['last_screen_x'] + (smooth_x - movement_state['last_screen_x']) * lerp_factor
                        cursor_y = movement_state['last_screen_y'] + (smooth_y - movement_state['last_screen_y']) * lerp_factor

                        if abs(cursor_x - movement_state['last_screen_x']) >= dead_zone_min or abs(cursor_y - movement_state['last_screen_y']) >= dead_zone_min:
                            pyautogui.moveTo(cursor_x, cursor_y)

                        movement_state['last_screen_x'], movement_state['last_screen_y'] = cursor_x, cursor_y
                        movement_state['last_index_x'], movement_state['last_index_y'] = index_tip.x, index_tip.y
                    elif is_right:
                        right_movement = {'last_screen_x': None, 'last_screen_y': None, 'last_index_x': None, 'last_index_y': None}

                    if dist_index_pouce < distance_pincement_min and main_stable and main_utilisable:
                        if temps_debut_pincement is None:
                            temps_debut_pincement = time.time()
                        elif (time.time() - temps_debut_pincement) >= temps_pincement_min:
                            if not clic_en_cours and (time.time() - temps_dernier_clic) > delai_clic:
                                if label == "Right":
                                    pyautogui.click()
                                elif label == "Left":
                                    pyautogui.rightClick()
                                clic_en_cours = True
                                temps_dernier_clic = time.time()
                    else:
                        temps_debut_pincement = None
                        clic_en_cours = False

                    majeur_levé = majeur_tip.y < majeur_pip.y
                    index_plié = index_tip.y > index_pip.y
                    annulaire_plié = hand_landmarks.landmark[16].y > annulaire_pip.y
                    auriculaire_plié = hand_landmarks.landmark[20].y > auriculaire_pip.y

                    if majeur_levé and index_plié and annulaire_plié and auriculaire_plié and main_utilisable:
                        os.system('osascript -e \'tell application "System Events" to keystroke "q" using {control down, command down}\'')
                        time.sleep(1)

                    doigts_fermes = [
                        index_tip.y > index_pip.y,
                        majeur_tip.y > majeur_pip.y,
                        hand_landmarks.landmark[16].y > annulaire_pip.y,
                        hand_landmarks.landmark[20].y > auriculaire_pip.y
                    ]

                    if all(doigt_ferme for doigt_ferme in doigts_fermes) and main_utilisable:
                        if time.time() - last_scroll_time > scroll_delay:
                            if label == "Right":
                                pyautogui.scroll(-scroll_amount)
                            elif label == "Left":
                                pyautogui.scroll(scroll_amount)
                            last_scroll_time = time.time()

                    tracking['last_index_x'] = index_tip.x
                    tracking['last_index_y'] = index_tip.y

            self.change_pixmap_signal.emit(frame)
            time.sleep(0.033)

        right_movement = {'last_screen_x': None, 'last_screen_y': None, 'last_index_x': None, 'last_index_y': None}
        right_tracking = {'last_index_x': None, 'last_index_y': None}
        left_tracking = {'last_index_x': None, 'last_index_y': None}
        kf_x = KalmanFilter1D()
        kf_y = KalmanFilter1D()
        clic_en_cours = False
        temps_debut_pincement = None
        temps_dernier_clic = 0
        last_scroll_time = 0

# ------------------------
# Widget personnalisé : fond animé en dégradé (amélioré avec plus de fluidité)
# ------------------------
class GradientWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.colors = [
            (90, 147, 255),   # Bleu
            (255, 105, 180),  # Rose
            (147, 112, 219),  # Violet
            (50, 205, 50),    # Vert
            (255, 165, 0),    # Orange (ajouté pour plus de variété)
        ]
        self.current_index = 0
        self.next_index = 1
        self.progress = 0.0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_gradient)
        self.timer.start(30)  # Plus fluide (toutes les 30ms)

    def update_gradient(self):
        self.progress += 0.01
        if self.progress >= 1.0:
            self.progress = 0.0
            self.current_index = (self.current_index + 1) % len(self.colors)
            self.next_index = (self.next_index + 1) % len(self.colors)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        c1 = QColor(*self.colors[self.current_index])
        c2 = QColor(*self.colors[self.next_index])
        gradient.setColorAt(0, c1.lighter(130))  # Plus clair pour un look plus vibrant
        gradient.setColorAt(1, c2.lighter(130))
        painter.fillRect(QRectF(0, 0, self.width(), self.height()), gradient)

# ------------------------
# Fenêtre principale (UI) - Frontend amélioré : plus petite, styles modernes, animations, etc.
# ------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Virtual Mouse Controller")
        self.setGeometry(200, 200, 400, 450)  # Fenêtre plus petite comme demandé

        # Icône de la fenêtre (ajout pour un look pro)
        self.setWindowIcon(QIcon.fromTheme("input-mouse"))

        self.gradient_widget = GradientWidget(self)
        self.setCentralWidget(self.gradient_widget)
        layout = QVBoxLayout(self.gradient_widget)
        layout.setSpacing(15)  # Espacement réduit pour fenêtre plus petite
        layout.setContentsMargins(20, 20, 20, 20)  # Marges plus serrées

        # Style global amélioré (thème sombre/modern avec transitions)
        self.setStyleSheet("""
            QMainWindow {
                font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
                background: transparent;
            }
            QLabel {
                color: #FFFFFF;
            }
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 8px;
                padding: 8px 16px;
                color: #FFFFFF;
                font-size: 14px;
                font-weight: 500;
                transition: background-color 0.3s ease;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.1);
            }
            QMenuBar {
                background-color: rgba(0, 0, 0, 0.5);
                color: #FFFFFF;
            }
            QMenuBar::item {
                background: transparent;
                padding: 4px 8px;
            }
            QMenuBar::item:selected {
                background: rgba(255, 255, 255, 0.2);
                border-radius: 4px;
            }
            QMenu {
                background-color: rgba(30, 30, 30, 0.9);
                color: #FFFFFF;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            QMenu::item:selected {
                background: rgba(255, 255, 255, 0.2);
            }
        """)

        # --------------------
        # MENU BAR (amélioré avec styles)
        # --------------------
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        help_menu = menubar.addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self.about)
        help_menu.addAction(about_action)

        # --------------------
        # HEADER (plus élégant, avec font bold)
        # --------------------
        header = QLabel("Virtual Mouse")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setFont(QFont("SF Pro Display", 20, QFont.Weight.Bold))
        header.setStyleSheet("""
            color: #FFFFFF;
            padding: 10px;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 10px;
        """)
        layout.addWidget(header)

        # --------------------
        # CONTRÔLES (bouton start/stop avec texte + icône, status avec couleur dynamique)
        # --------------------
        control_layout = QHBoxLayout()
        control_layout.setSpacing(10)

        self.start_button = QPushButton("Start")
        self.start_button.setIcon(QIcon.fromTheme("media-playback-start"))
        self.start_button.setIconSize(QSize(24, 24))
        self.start_button.setToolTip("Start/Stop Virtual Mouse")
        self.start_button.clicked.connect(self.toggle_virtual_mouse)
        control_layout.addWidget(self.start_button)

        self.status_label = QLabel("Stopped")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            font-size: 14px;
            color: #FF4D4D;  /* Rouge pour stopped */
            background-color: rgba(0, 0, 0, 0.4);
            padding: 6px 12px;
            border-radius: 8px;
            font-weight: 500;
        """)
        control_layout.addWidget(self.status_label)

        layout.addLayout(control_layout)

        # --------------------
        # AFFICHAGE VIDÉO (plus petit, avec bordure arrondie et ombre)
        # --------------------
        self.video_label = QLabel()
        self.video_label.setFixedSize(320, 240)  # Réduit pour fenêtre plus petite
        self.video_label.setStyleSheet("""
            background-color: rgba(0, 0, 0, 0.5);
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
        """)
        layout.addWidget(self.video_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # --------------------
        # INFOS GESTES (amélioré : plus compact, scrollable si besoin, hover effect)
        # --------------------
        self.info_label = QLabel(
            "Gestures:\n"
            "• Cursor: Right hand, index up\n"
            "• Left Click: Right pinch\n"
            "• Right Click: Left pinch\n"
            "• Scroll Up: Left fist\n"
            "• Scroll Down: Right fist\n"
            "• Lock: Middle finger up"
        )
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("""
            font-size: 13px;
            font-weight: 400;
            color: #E0E0E0;
            background: qlineargradient(
                x1: 0, y1: 0, x2: 1, y2: 1,
                stop: 0 rgba(50, 50, 50, 200),
                stop: 1 rgba(20, 20, 20, 200)
            );
            padding: 10px 15px;
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.15);
            box-shadow: 0 3px 8px rgba(0, 0, 0, 0.25);
            line-height: 1.5;
            transition: background 0.3s ease;
        """)
        self.info_label.setToolTip("Hand gestures for control")
        layout.addWidget(self.info_label)

        # Ajout d'une animation fade-in pour l'info_label (plein d'autres trucs)
        self.animate_fade_in(self.info_label)

        # --------------------
        # FOOTER (plus discret)
        # --------------------
        footer = QLabel("© 2025 VMC Project")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet("""
            font-size: 11px;
            color: #BBBBBB;
            padding: 5px;
        """)
        layout.addWidget(footer)

        self.thread = VideoThread()
        self.thread.change_pixmap_signal.connect(self.update_image)

    # --------------------
    # Animation fade-in (ajout pour un look plus dynamique)
    # --------------------
    def animate_fade_in(self, widget):
        animation = QPropertyAnimation(widget, b"opacity")
        animation.setDuration(1000)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        animation.start()

    # Note: Pour opacity, on doit override paintEvent si besoin, mais pour simplicité, on utilise avec QLabel

    def toggle_virtual_mouse(self):
        if not self.thread.running:
            self.thread.running = True
            self.thread.start()
            self.status_label.setText("Running")
            self.status_label.setStyleSheet(self.status_label.styleSheet().replace("#FF4D4D", "#4DFF4D"))  # Vert pour running
            self.start_button.setText("Stop")
            self.start_button.setIcon(QIcon.fromTheme("media-playback-stop"))
            self.start_button.setToolTip("Stop Virtual Mouse")
            # Animation scale pour bouton
            self.animate_button(self.start_button)
        else:
            self.thread.running = False
            self.thread.wait()
            self.status_label.setText("Stopped")
            self.status_label.setStyleSheet(self.status_label.styleSheet().replace("#4DFF4D", "#FF4D4D"))
            self.start_button.setText("Start")
            self.start_button.setIcon(QIcon.fromTheme("media-playback-start"))
            self.start_button.setToolTip("Start Virtual Mouse")
            self.animate_button(self.start_button)

    # --------------------
    # Animation pour bouton (scale bounce)
    # --------------------
    def animate_button(self, button):
        animation = QPropertyAnimation(button, b"geometry")
        animation.setDuration(200)
        start_rect = button.geometry()
        animation.setStartValue(start_rect)
        mid_rect = start_rect.adjusted(-2, -2, 4, 4)
        animation.setKeyValueAt(0.5, mid_rect)
        animation.setEndValue(start_rect)
        animation.setEasingCurve(QEasingCurve.Type.InOutBounce)
        animation.start()

    def update_image(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        qimg = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888).scaled(320, 240, Qt.AspectRatioMode.KeepAspectRatio)
        self.video_label.setPixmap(QPixmap.fromImage(qimg))

    def about(self):
        about_text = (
            "Virtual Mouse Controller\n"
            "Version 2.0 - Enhanced UI\n"
            "Control your mouse with hand gestures via webcam.\n"
            "Powered by MediaPipe & PyQt6\n"
            "© 2025 Virtual Mouse Project"
        )
        QMessageBox.about(self, "About Virtual Mouse", about_text)

    def closeEvent(self, event):
        self.thread.running = False
        self.thread.wait()
        cap.release()
        cv2.destroyAllWindows()
        event.accept()

# ------------------------
# MAIN
# ------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())