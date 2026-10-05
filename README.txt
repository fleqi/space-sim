===============================================================================================

Tarea 3 - Felipe Cabezas
Simulador espacial

===============================================================================================

RESUMEN:

Es un simulador inspirado en KSP y SFS, donde se maneja una vaca alien y se pueden probar maniobras orbitales básicas. Las simulaciones son en base a esferas de influencia, lo que permite ahorrar cálculos, los que son hechos con la fórmula de la gravitación universal. Se usó IA para ajustar números como distancias y radios (para que fuera mas jugable), además de una ayuda visual (estela), que lo hace ver más bonito y me ayudó a debuggear las órbitas, verificando que se conservara la energía (no cambiaran significativamente) y que las esferas de influencia se respetaran.

Idealmente correr en el entorno virtual que se usó en el curso, todas las otras librerías son tomadas de ahi, aunque las específicas del curso vienen en el mismo zip, lo importante son las instaladas con pip.

https://youtu.be/gGd7_kGkFjQ

===============================================================================================

CONTROLES:

	SPACE o UP (flecha arriba): Acelerar en progrado (siguiendo trayectoria) 
	SHIFT o DOWN: Desacelerar (o acelerar en retrogrado)
	1: Cámara libre
	2: Cámara siguiendo nave
	3: Cámara siguiendo cuerpo dominante

	En cámara libre:
	WASD: Movimiento
	MOUSE: Apuntado

	En las otras cámaras:
	MOUSE: Apuntado
	SCROLL: Acercamiento y alejamiento

===============================================================================================

PUNTAJES BUSCADOS:

Iluminación (4.0):
	- Blinn-Phong: Usando los shaders del curso
	- Point Light: Para el sol
Modelos, Mallas y Entorno (4.0):
	- Carga de Mallas Complejas (.obj): Vaca y esferas
	- Manejo de Materiales Diferenciados: Se variaron los parámetros de material para el modelo phong, según el tipo de planeta, además, se creó un shader específico para el sol.
Física, Colisiones e Interacción (4.0):
	- Sistema de Colisiones: Al chocar con un planeta, la nave se detiene y se imprime en la consola
	- Cinemática / Gravedad / Físicas: Implementación de gravedad y maniobras orbitales usando velocity verlet
Misceláneo (1.0):
	- Manejo de múltiples cámaras: Las 3 cámaras disponibles

No estoy seguro de cómo se relacionan los otros items, pero eso es lo que pude reconocer.
La implementación es en 3D pero todo ocurre en un sistema planar, por lo que es más como un 2.5D.

===============================================================================================

BLAH BLAH (ayuda para el video):

La idea era hacer un simulador tipo Kerbal Space Program o Spaceflight Simulator, aunque me emocioné mucho añadiendole cosas que en realidad no eran necesarias. De cualquier manera, como son mis juegos favoritos, fue muy divertido trabajar en el programa, aunque puede que hayan quedado muchos bugs y cosas por implementar que ayudarían a hacerlo mas divertido.

La nave podría ser reemplazada por un modelo real, pero pensé que sería más rápido usar el modelo de vaca y pintarla verde, así que ahora es una vaca alien (método de propulsión desconocido).
La vaca alien se maneja con el espacio y el shift, o alternativamente la flecha hacia arriba y la flecha hacia abajo, que permiten la aceleración y desaceleración respectivamente, lo que se hace con respecto a la trayectoria actual, por lo que es imposible hacer cosas como desplazar la órbita, ya que necesitaríamos propulsión hacia la derecha o izqierda.

En el zip vienen todas las librerias del curso, si bien ocupa mas espacio, resultaba mucho más fácil trabajar con las rutas de esa manera. De igual forma, todas las otras librerías vienen del venv del curso, por lo que lo ideal es ejecutarlo en ese entorno. Hice una pequeña modificación a la librería de cámaras, aumentando el rango de corte, porque a la escala a la que hice el programa no se podía ver todo el sistema.

El programa inicia con trayectoria al planeta 2 (similar a Marte o Duna del KSP), donde será capturado y luego chocará, la forma de evitar la colisión es acelerando al momento de la captura para que la orbita pase al lado, y frenando al llegar a periapsis (punto más bajo de la órbita). Se puede modificar la posición inicial, pero para efectos de prueba, esas condiciones me resultaron perfectas.

Se tienen 3 cámaras, la libre, siguiendo a la nave y siguiendo al cuerpo dominante, asociadas a las teclas 1, 2 y 3 respectivamente. La cámara libre permite moverse con WASD y mover el mouse para el apuntado, mientras que las otras dos son del tipo órbita, enfocan siempre al centro del cuerpo deseado y se manejan con el mouse para rotar y con la ruedita para acercarse y alejarse, en la implementación de esto último le pedí ayuda a la IA al no saber la sintáxis, pero se usó la OrbitCam de la libreria en utils.

Los planetas tienen gravedad simulada respecto al sol (calcular para todos los otros planetas sería muy caro e inestable), además, todos los cuerpos tienen una esfera de influencia con un radio definido, que sirve para definir cuándo vale la pena hacer los cálculos respecto a ese  planeta o no.

Se implementó una estela que permite visualizar mejor las órbitas, los detalles no los manejo extremadamente bien, pues al ser algo fuera del puntaje y servir como una ayuda visual para debugging, se lo pedí a la IA, es posible modificar algunos parámetros como MAX_TRAIL_POINTS y TRAIL_SAMPLE_EVERY, que cambian el máximo de puntos y cada cuántos frames se actualizan, por defecto quedaron en 1200 y 1 respectivamente (aprox. linea 390).

La rapidez de la simulación se puede modificar, siempre corre a 60 fps, pero los saltos son multiplicados por la variable time_scale, que tiene como piso 0.1 y techo infinito, al igual que en KSP, mientras más lento mejor simulado. time_scale se reduce con la tecla Q y aumenta con la tecla E, sumando o restando 0.1 cada vez.
