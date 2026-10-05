# Simulador espacial

## Resumen

Es un simulador inspirado en KSP y SFS, donde se maneja una vaca alien y se pueden probar maniobras orbitales básicas. Las simulaciones son en base a esferas de influencia, lo que permite ahorrar cálculos, los que son hechos con la fórmula de la gravitación universal. Se usó IA para ajustar números como distancias y radios (para que fuera mas jugable), además de una ayuda visual (estela), que lo hace ver más bonito y me ayudó a debuggear las órbitas, verificando que se conservara la energía (no cambiaran significativamente) y que las esferas de influencia se respetaran.

Este proyecto se hizo como Tarea 3 para el ramo de Modelación y Computación Gráfica para Ingenieros - CC3501 (Otoño 2026).

## Video

[![Video del simulador](https://img.youtube.com/vi/gGd7_kGkFjQ/hqdefault.jpg)](https://youtu.be/gGd7_kGkFjQ)

## Ejecución

Requiere Python 3 y una GPU con soporte para OpenGL.

En Linux o macOS, el script `run.sh` crea un entorno virtual, instala las dependencias y abre el simulador:

```bash
./run.sh
```

De forma manual (incluye Windows):

```bash
python -m venv .venv
source .venv/bin/activate        # en Windows: .venv\Scripts\activate
pip install -r requirements.txt
python Tarea3.py
```

## Controles

| Tecla | Acción |
|---|---|
| `E` | Acelera el tiempo (+0.1x a la velocidad de simulación) |
| `Q` | Desacelera el tiempo (−0.1x, mínimo 0.1x) |
| `SPACE` o `↑` | Acelerar en progrado (siguiendo trayectoria) |
| `SHIFT` o `↓` | Desacelerar (o acelerar en retrógrado) |
| `1` | Cámara libre |
| `2` | Cámara siguiendo nave |
| `3` | Cámara siguiendo cuerpo dominante |

**En cámara libre:**

| Control | Acción |
|---|---|
| `WASD` | Movimiento |
| Mouse | Apuntado |

**En las otras cámaras:**

| Control | Acción |
|---|---|
| Mouse | Apuntado |
| Scroll | Acercamiento y alejamiento |

## Uso de IA

Claude se usó para implementar las líneas de trayectoria y ayudar a visualizar la lógica que quedaba por implementar. También se usó para facilitar la ejecución del programa y transcribir el README.txt a README.md
