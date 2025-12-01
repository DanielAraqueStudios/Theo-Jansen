# 🦿 Simulador Interactivo Mecanismo Theo Jansen

Aplicación con interfaz gráfica moderna (PyQt6) para visualizar y analizar el mecanismo caminante tipo Theo Jansen en tiempo real.

## ✨ Características

- 🎨 **Interfaz Dark Mode** moderna y profesional
- 📊 **Visualización en tiempo real** del mecanismo
- ⚙️ **Controles interactivos** para ajustar longitudes de eslabones
- 🎬 **Animación fluida** con control de velocidad
- 📏 **Mediciones automáticas** de longitud y altura de paso
- 🔄 **Vista de trayectoria completa** del pie
- 🎯 **Proporciones clásicas** de Theo Jansen preconfiguradas

## 📋 Requisitos

- Python 3.10 o superior
- PyQt6
- Matplotlib
- NumPy
- SciPy

## 🚀 Instalación

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

O instalar manualmente:

```bash
pip install PyQt6 matplotlib numpy scipy
```

### 2. Ejecutar el simulador

```bash
python simulador_jansen_gui.py
```

## 🎮 Uso

### Panel de Control

**Control de Animación:**
- ▶️ **Iniciar/Pausar**: Activa la animación continua del mecanismo
- 🔄 **Reiniciar**: Vuelve al ángulo inicial (0°)
- **Ángulo Manual**: Slider para mover manualmente el mecanismo
- **Velocidad**: Ajusta la velocidad de la animación

**Longitudes de Eslabones:**
- Ajusta cada eslabón individualmente (10-200 mm)
- **Factor de Escala**: Multiplica todas las longitudes uniformemente
- **Restaurar Originales**: Vuelve a las proporciones de Theo Jansen

### Visualización

- **Eslabones en colores**: Cada componente tiene un color distintivo
- **Trayectoria cian**: Muestra el camino completo del pie
- **Puntos fijos**: Marcados en rojo (A) y verde (B)
- **Pie amarillo**: Punto de contacto con el suelo
- **Línea de suelo**: Referencia horizontal en y=0

### Información

El panel muestra:
- **Longitud de paso**: Distancia horizontal del ciclo de marcha
- **Altura de paso**: Elevación máxima del pie
- **Posición actual**: Coordenadas instantáneas del pie

## 📐 Proporciones de Theo Jansen

Las proporciones originales (en mm) son:

| Eslabón | Nombre | Longitud |
|---------|--------|----------|
| a | Manivela | 38.0 |
| b | Acoplador 1 | 41.5 |
| c | Acoplador 2 | 39.3 |
| d | Acoplador 3 | 40.1 |
| e | Balancín 1 | 55.8 |
| f | Balancín 2 | 39.4 |
| g | Ternario 1 | 36.7 |
| h | Ternario 2 | 65.7 |

Factor de escala por defecto: **5.0**

## 🔧 Personalización

### Modificar colores de eslabones

Edita los colores en la función `actualizar_grafico()`:

```python
self.graficar_eslabon(puntos['A'], puntos['C'], '#ff6b6b', 'Manivela')
```

### Ajustar rango de visualización

Modifica en `actualizar_grafico()`:

```python
self.canvas.axes.set_xlim(-100, 300)
self.canvas.axes.set_ylim(-150, 150)
```

### Cambiar resolución de trayectoria

En `calcular_trayectoria()`:

```python
def calcular_trayectoria(self, n_puntos=360):  # Más puntos = mayor suavidad
```

## 🐛 Solución de Problemas

### Error: "No module named 'PyQt6'"
```bash
pip install PyQt6
```

### Error: "convergence error" en scipy
- Reducir el factor de escala
- Verificar que las longitudes sean físicamente posibles
- Evitar valores extremos (muy pequeños o muy grandes)

### Animación lenta
- Reducir la resolución de trayectoria (n_puntos)
- Cerrar otras aplicaciones pesadas
- Aumentar slider de velocidad

## 📚 Referencias

- [Theo Jansen - Strandbeest](https://www.strandbeest.com/)
- Norton, R.L. "Diseño de Maquinaria"
- Documentación PyQt6
- Matplotlib Documentation

## 👥 Autores

- Sebastián Andrés Rodríguez Carrillo
- David Andrés Rodríguez Rozo
- Daniel García Araque

**Universidad Militar Nueva Granada**  
Ingeniería Mecatrónica - Dinámica Aplicada  
2025

## 📄 Licencia

Proyecto académico - Universidad Militar Nueva Granada
