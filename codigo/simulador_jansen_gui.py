"""
Simulador Interactivo del Mecanismo Theo Jansen
PyQt6 + Matplotlib con Dark Mode UI/UX

Permite ajustar dimensiones de eslabones en tiempo real y visualizar
la animación del mecanismo con análisis cinemático.
"""

import sys
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QSlider, QLabel, QPushButton, 
                             QGroupBox, QGridLayout, QSpinBox, QDoubleSpinBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPalette, QColor
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from scipy.optimize import fsolve

class MecanismoJansen:
    """Clase para cálculos cinemáticos del mecanismo Theo Jansen"""
    
    def __init__(self):
        # Proporciones originales de Theo Jansen (en mm)
        self.L = {
            'a': 38.0,   # Manivela
            'b': 41.5,   # Acoplador 1
            'c': 39.3,   # Acoplador 2
            'd': 40.1,   # Acoplador 3
            'e': 55.8,   # Balancín 1
            'f': 39.4,   # Balancín 2
            'g': 36.7,   # Ternario 1
            'h': 65.7,   # Ternario 2
            'm': 7.8,    # Offset horizontal punto fijo
            'n': 25.0    # Offset vertical punto fijo
        }
        
        # Factor de escala
        self.escala = 5.0
        self.aplicar_escala()
        
    def aplicar_escala(self):
        """Aplica el factor de escala a todas las longitudes"""
        self.L_scaled = {k: v * self.escala for k, v in self.L.items()}
        
    def actualizar_longitud(self, nombre, valor):
        """Actualiza una longitud específica"""
        self.L[nombre] = valor
        self.aplicar_escala()
        
    def resolver_cinematica(self, theta):
        """
        Resuelve la cinemática del mecanismo para un ángulo dado
        Retorna las posiciones de todos los puntos clave
        """
        L = self.L_scaled
        
        # Punto fijo A (origen de la manivela)
        A = np.array([0, 0])
        
        # Punto fijo B (segundo punto fijo)
        B = np.array([L['m'], L['n']])
        
        # Punto C (extremo de la manivela)
        C = A + np.array([L['a'] * np.cos(theta), L['a'] * np.sin(theta)])
        
        # Resolver sistema de ecuaciones para encontrar otros puntos
        # Este es un sistema simplificado - en realidad es más complejo
        
        # Punto D (conexión intermedia)
        def ecuaciones_D(vars):
            Dx, Dy = vars
            D = np.array([Dx, Dy])
            eq1 = np.linalg.norm(D - C) - L['b']  # |DC| = b
            eq2 = np.linalg.norm(D - B) - L['c']  # |DB| = c
            return [eq1, eq2]
        
        # Estimación inicial
        D_init = C + np.array([L['b'], 0])
        D_sol = fsolve(ecuaciones_D, D_init)
        D = np.array(D_sol)
        
        # Punto E (siguiente conexión)
        def ecuaciones_E(vars):
            Ex, Ey = vars
            E = np.array([Ex, Ey])
            eq1 = np.linalg.norm(E - D) - L['d']
            eq2 = np.linalg.norm(E - B) - L['e']
            return [eq1, eq2]
        
        E_init = D + np.array([L['d'], -L['d']/2])
        E_sol = fsolve(ecuaciones_E, E_init)
        E = np.array(E_sol)
        
        # Punto F (pie del mecanismo)
        def ecuaciones_F(vars):
            Fx, Fy = vars
            F = np.array([Fx, Fy])
            eq1 = np.linalg.norm(F - E) - L['f']
            eq2 = np.linalg.norm(F - D) - L['g']
            return [eq1, eq2]
        
        F_init = E + np.array([L['f'], -L['f']])
        F_sol = fsolve(ecuaciones_F, F_init)
        F = np.array(F_sol)
        
        return {
            'A': A, 'B': B, 'C': C, 'D': D, 'E': E, 'F': F
        }
    
    def calcular_trayectoria(self, n_puntos=360):
        """Calcula la trayectoria completa del pie"""
        thetas = np.linspace(0, 2*np.pi, n_puntos)
        trayectoria = []
        
        for theta in thetas:
            try:
                puntos = self.resolver_cinematica(theta)
                trayectoria.append(puntos['F'])
            except:
                trayectoria.append(np.array([np.nan, np.nan]))
        
        return np.array(trayectoria)


class MplCanvas(FigureCanvas):
    """Canvas de Matplotlib con tema oscuro"""
    
    def __init__(self, parent=None, width=8, height=6, dpi=100):
        # Configurar estilo oscuro
        plt.style.use('dark_background')
        
        self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor='#2b2b2b')
        self.axes = self.fig.add_subplot(111)
        self.axes.set_facecolor('#1e1e1e')
        self.axes.grid(True, alpha=0.2, color='#404040')
        
        super().__init__(self.fig)
        self.setParent(parent)


class SimuladorJansenGUI(QMainWindow):
    """Ventana principal de la aplicación"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simulador Mecanismo Theo Jansen - UMNG Mecatrónica")
        self.setGeometry(100, 100, 1400, 900)
        
        # Configurar tema oscuro
        self.setup_dark_theme()
        
        # Inicializar mecanismo
        self.mecanismo = MecanismoJansen()
        self.theta_actual = 0
        self.animacion_activa = False
        
        # Configurar UI
        self.setup_ui()
        
        # Timer para animación
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar_animacion)
        self.velocidad_animacion = 50  # ms
        
        # Graficar estado inicial
        self.actualizar_grafico()
        
    def setup_dark_theme(self):
        """Configura el tema oscuro de la aplicación"""
        palette = QPalette()
        
        # Colores del tema oscuro
        palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(220, 220, 220))
        palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(45, 45, 45))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(220, 220, 220))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(220, 220, 220))
        palette.setColor(QPalette.ColorRole.Text, QColor(220, 220, 220))
        palette.setColor(QPalette.ColorRole.Button, QColor(45, 45, 45))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(220, 220, 220))
        palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))
        
        self.setPalette(palette)
        
        # Stylesheet adicional
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QGroupBox {
                border: 2px solid #404040;
                border-radius: 5px;
                margin-top: 10px;
                padding: 15px;
                font-weight: bold;
                color: #e0e0e0;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 11pt;
            }
            QPushButton {
                background-color: #2a82da;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #3d95e8;
            }
            QPushButton:pressed {
                background-color: #1e6fba;
            }
            QPushButton:disabled {
                background-color: #404040;
                color: #808080;
            }
            QSlider::groove:horizontal {
                border: 1px solid #404040;
                height: 8px;
                background: #2b2b2b;
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #2a82da;
                border: 1px solid #1e6fba;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QSlider::handle:horizontal:hover {
                background: #3d95e8;
            }
            QDoubleSpinBox, QSpinBox {
                background-color: #2b2b2b;
                border: 1px solid #404040;
                border-radius: 3px;
                padding: 5px;
                color: #e0e0e0;
            }
        """)
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QHBoxLayout(central_widget)
        
        # Panel izquierdo (controles)
        panel_izquierdo = QWidget()
        panel_izquierdo.setMaximumWidth(400)
        panel_izquierdo.setMinimumWidth(350)
        layout_izquierdo = QVBoxLayout(panel_izquierdo)
        
        # Título
        titulo = QLabel("🦿 Mecanismo Theo Jansen")
        titulo.setStyleSheet("font-size: 18pt; font-weight: bold; color: #2a82da; padding: 10px;")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_izquierdo.addWidget(titulo)
        
        # Grupo de controles de animación
        grupo_animacion = self.crear_grupo_animacion()
        layout_izquierdo.addWidget(grupo_animacion)
        
        # Grupo de longitudes de eslabones
        grupo_eslabones = self.crear_grupo_eslabones()
        layout_izquierdo.addWidget(grupo_eslabones)
        
        # Grupo de información
        grupo_info = self.crear_grupo_informacion()
        layout_izquierdo.addWidget(grupo_info)
        
        layout_izquierdo.addStretch()
        
        # Panel derecho (gráficos)
        panel_derecho = QWidget()
        layout_derecho = QVBoxLayout(panel_derecho)
        
        # Canvas de Matplotlib
        self.canvas = MplCanvas(self, width=8, height=6, dpi=100)
        layout_derecho.addWidget(self.canvas)
        
        # Agregar paneles al layout principal
        main_layout.addWidget(panel_izquierdo)
        main_layout.addWidget(panel_derecho)
        
    def crear_grupo_animacion(self):
        """Crea el grupo de controles de animación"""
        grupo = QGroupBox("⚙️ Control de Animación")
        layout = QVBoxLayout()
        
        # Botón play/pause
        self.btn_play = QPushButton("▶️ Iniciar Animación")
        self.btn_play.clicked.connect(self.toggle_animacion)
        layout.addWidget(self.btn_play)
        
        # Botón reset
        btn_reset = QPushButton("🔄 Reiniciar")
        btn_reset.clicked.connect(self.reiniciar_animacion)
        layout.addWidget(btn_reset)
        
        # Slider de ángulo manual
        layout.addWidget(QLabel("Ángulo Manual (°):"))
        self.slider_angulo = QSlider(Qt.Orientation.Horizontal)
        self.slider_angulo.setMinimum(0)
        self.slider_angulo.setMaximum(360)
        self.slider_angulo.setValue(0)
        self.slider_angulo.valueChanged.connect(self.cambiar_angulo_manual)
        layout.addWidget(self.slider_angulo)
        
        self.label_angulo = QLabel("0°")
        self.label_angulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label_angulo)
        
        # Slider de velocidad
        layout.addWidget(QLabel("Velocidad de Animación:"))
        slider_velocidad = QSlider(Qt.Orientation.Horizontal)
        slider_velocidad.setMinimum(1)
        slider_velocidad.setMaximum(10)
        slider_velocidad.setValue(5)
        slider_velocidad.valueChanged.connect(self.cambiar_velocidad)
        layout.addWidget(slider_velocidad)
        
        grupo.setLayout(layout)
        return grupo
    
    def crear_grupo_eslabones(self):
        """Crea el grupo de controles de longitudes de eslabones"""
        grupo = QGroupBox("📏 Longitudes de Eslabones (mm)")
        layout = QGridLayout()
        
        # Diccionario de nombres descriptivos
        nombres = {
            'a': 'Manivela',
            'b': 'Acoplador 1',
            'c': 'Acoplador 2',
            'd': 'Acoplador 3',
            'e': 'Balancín 1',
            'f': 'Balancín 2',
            'g': 'Ternario 1',
            'h': 'Ternario 2'
        }
        
        self.spinboxes = {}
        row = 0
        
        for clave, nombre in nombres.items():
            label = QLabel(f"{clave.upper()}: {nombre}")
            spinbox = QDoubleSpinBox()
            spinbox.setMinimum(10.0)
            spinbox.setMaximum(200.0)
            spinbox.setValue(self.mecanismo.L[clave])
            spinbox.setSuffix(" mm")
            spinbox.setDecimals(1)
            spinbox.setSingleStep(0.5)
            spinbox.valueChanged.connect(lambda v, k=clave: self.actualizar_longitud(k, v))
            
            layout.addWidget(label, row, 0)
            layout.addWidget(spinbox, row, 1)
            
            self.spinboxes[clave] = spinbox
            row += 1
        
        # Botón para restaurar proporciones originales
        btn_restaurar = QPushButton("↺ Restaurar Originales")
        btn_restaurar.clicked.connect(self.restaurar_originales)
        layout.addWidget(btn_restaurar, row, 0, 1, 2)
        
        # Factor de escala
        row += 1
        layout.addWidget(QLabel("Factor de Escala:"), row, 0)
        self.spinbox_escala = QDoubleSpinBox()
        self.spinbox_escala.setMinimum(1.0)
        self.spinbox_escala.setMaximum(10.0)
        self.spinbox_escala.setValue(self.mecanismo.escala)
        self.spinbox_escala.setDecimals(1)
        self.spinbox_escala.setSingleStep(0.5)
        self.spinbox_escala.valueChanged.connect(self.actualizar_escala)
        layout.addWidget(self.spinbox_escala, row, 1)
        
        grupo.setLayout(layout)
        return grupo
    
    def crear_grupo_informacion(self):
        """Crea el grupo de información del mecanismo"""
        grupo = QGroupBox("📊 Información del Mecanismo")
        layout = QVBoxLayout()
        
        self.label_longitud_paso = QLabel("Longitud de paso: -- cm")
        self.label_altura_paso = QLabel("Altura de paso: -- cm")
        self.label_posicion_pie = QLabel("Posición pie: (0.0, 0.0) cm")
        
        layout.addWidget(self.label_longitud_paso)
        layout.addWidget(self.label_altura_paso)
        layout.addWidget(self.label_posicion_pie)
        
        # Información del proyecto
        layout.addWidget(QLabel(""))
        info = QLabel("Universidad Militar Nueva Granada\n"
                     "Ingeniería Mecatrónica\n"
                     "Dinámica Aplicada - 2025")
        info.setStyleSheet("color: #808080; font-size: 9pt;")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)
        
        grupo.setLayout(layout)
        return grupo
    
    def toggle_animacion(self):
        """Activa/desactiva la animación"""
        self.animacion_activa = not self.animacion_activa
        
        if self.animacion_activa:
            self.btn_play.setText("⏸️ Pausar Animación")
            self.timer.start(self.velocidad_animacion)
            self.slider_angulo.setEnabled(False)
        else:
            self.btn_play.setText("▶️ Iniciar Animación")
            self.timer.stop()
            self.slider_angulo.setEnabled(True)
    
    def reiniciar_animacion(self):
        """Reinicia la animación desde el inicio"""
        self.theta_actual = 0
        self.slider_angulo.setValue(0)
        self.actualizar_grafico()
    
    def actualizar_animacion(self):
        """Actualiza el frame de la animación"""
        self.theta_actual += np.deg2rad(2)
        if self.theta_actual >= 2 * np.pi:
            self.theta_actual = 0
        
        self.slider_angulo.setValue(int(np.rad2deg(self.theta_actual)))
        self.actualizar_grafico()
    
    def cambiar_angulo_manual(self, valor):
        """Cambia el ángulo manualmente con el slider"""
        if not self.animacion_activa:
            self.theta_actual = np.deg2rad(valor)
            self.label_angulo.setText(f"{valor}°")
            self.actualizar_grafico()
    
    def cambiar_velocidad(self, valor):
        """Cambia la velocidad de la animación"""
        self.velocidad_animacion = int(100 / valor)
        if self.animacion_activa:
            self.timer.setInterval(self.velocidad_animacion)
    
    def actualizar_longitud(self, clave, valor):
        """Actualiza una longitud de eslabón"""
        self.mecanismo.actualizar_longitud(clave, valor)
        self.actualizar_grafico()
    
    def actualizar_escala(self, valor):
        """Actualiza el factor de escala"""
        self.mecanismo.escala = valor
        self.mecanismo.aplicar_escala()
        self.actualizar_grafico()
    
    def restaurar_originales(self):
        """Restaura las proporciones originales de Theo Jansen"""
        proporciones_originales = {
            'a': 38.0, 'b': 41.5, 'c': 39.3, 'd': 40.1,
            'e': 55.8, 'f': 39.4, 'g': 36.7, 'h': 65.7
        }
        
        for clave, valor in proporciones_originales.items():
            self.spinboxes[clave].setValue(valor)
            self.mecanismo.actualizar_longitud(clave, valor)
        
        self.actualizar_grafico()
    
    def actualizar_grafico(self):
        """Actualiza el gráfico del mecanismo"""
        try:
            # Limpiar gráfico
            self.canvas.axes.clear()
            
            # Calcular posiciones actuales
            puntos = self.mecanismo.resolver_cinematica(self.theta_actual)
            
            # Calcular trayectoria completa
            trayectoria = self.mecanismo.calcular_trayectoria()
            
            # Graficar trayectoria del pie
            self.canvas.axes.plot(trayectoria[:, 0], trayectoria[:, 1], 
                                 'c--', alpha=0.5, linewidth=1.5, label='Trayectoria del pie')
            
            # Graficar eslabones
            self.graficar_eslabon(puntos['A'], puntos['C'], '#ff6b6b', 'Manivela')
            self.graficar_eslabon(puntos['C'], puntos['D'], '#4ecdc4', 'Acoplador 1')
            self.graficar_eslabon(puntos['D'], puntos['B'], '#45b7d1', 'Acoplador 2')
            self.graficar_eslabon(puntos['B'], puntos['E'], '#96ceb4', 'Balancín')
            self.graficar_eslabon(puntos['D'], puntos['E'], '#ffeaa7', 'Conexión')
            self.graficar_eslabon(puntos['E'], puntos['F'], '#dfe6e9', 'Ternario')
            self.graficar_eslabon(puntos['D'], puntos['F'], '#fab1a0', 'Pie')
            
            # Graficar puntos fijos
            self.canvas.axes.plot(*puntos['A'], 'rs', markersize=12, label='Punto fijo A')
            self.canvas.axes.plot(*puntos['B'], 'gs', markersize=12, label='Punto fijo B')
            
            # Graficar articulaciones
            for nombre, punto in puntos.items():
                if nombre not in ['A', 'B']:
                    self.canvas.axes.plot(*punto, 'wo', markersize=8)
            
            # Graficar pie (punto F)
            self.canvas.axes.plot(*puntos['F'], 'yo', markersize=15, 
                                 markeredgecolor='orange', markeredgewidth=2, label='Pie')
            
            # Línea del suelo
            xlim = self.canvas.axes.get_xlim()
            self.canvas.axes.axhline(y=0, color='#404040', linestyle='-', linewidth=2, alpha=0.5)
            
            # Configuración del gráfico
            self.canvas.axes.set_xlim(-100, 300)
            self.canvas.axes.set_ylim(-150, 150)
            self.canvas.axes.set_aspect('equal')
            self.canvas.axes.grid(True, alpha=0.2, color='#404040')
            self.canvas.axes.set_xlabel('Posición X (mm)', color='#e0e0e0', fontsize=11)
            self.canvas.axes.set_ylabel('Posición Y (mm)', color='#e0e0e0', fontsize=11)
            self.canvas.axes.set_title(f'Mecanismo Theo Jansen - Ángulo: {np.rad2deg(self.theta_actual):.1f}°', 
                                      color='#2a82da', fontsize=14, fontweight='bold')
            self.canvas.axes.legend(loc='upper right', fontsize=8, framealpha=0.8)
            
            # Actualizar información
            self.actualizar_informacion(trayectoria, puntos['F'])
            
            # Redibujar
            self.canvas.draw()
            
        except Exception as e:
            print(f"Error al graficar: {e}")
    
    def graficar_eslabon(self, p1, p2, color, label=''):
        """Grafica un eslabón entre dos puntos"""
        self.canvas.axes.plot([p1[0], p2[0]], [p1[1], p2[1]], 
                             color=color, linewidth=3, alpha=0.8)
    
    def actualizar_informacion(self, trayectoria, pie):
        """Actualiza los labels de información"""
        # Calcular longitud de paso (máx - mín en x)
        longitud_paso = (np.nanmax(trayectoria[:, 0]) - np.nanmin(trayectoria[:, 0])) / 10  # a cm
        
        # Calcular altura de paso (máx en y)
        altura_paso = np.nanmax(trayectoria[:, 1]) / 10  # a cm
        
        # Actualizar labels
        self.label_longitud_paso.setText(f"Longitud de paso: {longitud_paso:.2f} cm")
        self.label_altura_paso.setText(f"Altura de paso: {altura_paso:.2f} cm")
        self.label_posicion_pie.setText(f"Posición pie: ({pie[0]/10:.2f}, {pie[1]/10:.2f}) cm")


def main():
    app = QApplication(sys.argv)
    
    # Configurar fuente de la aplicación
    from PyQt6.QtGui import QFont
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    ventana = SimuladorJansenGUI()
    ventana.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
