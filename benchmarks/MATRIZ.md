# Matriz de verificación y comparación

Se compara Dijkstra clásico (selección lineal del mínimo) con el Dijkstra con heap
existente. El formato del grafo, el origen 0 y la tarea (todas las distancias y
predecesores) son iguales dentro de cada comparación. No se comparan lenguajes.

## Rendimiento: hipótesis antes de medir

| ID / familia | Tamaños | Construcción | Qué pone a prueba | Hipótesis, no conclusión |
|---|---|---|---|---|
| P01 `tiny` | V=1,4,8,16 | Cadena con pesos 1..100 | Costos constantes | Las diferencias absolutas serán pequeñas; no asumir una mejora práctica |
| P02 `chain` | V=128,512,2048 | E=V−1, cadena dirigida | Heap con frontera de tamaño 1 | El clásico paga búsquedas cuadráticas; heap crece casi linealmente |
| P03 `star` | V=128,512,2048 | E=V−1, origen conectado a todos | Frontera grande sin mejoras posteriores | Heap evita selección lineal, pero requiere espacio para la frontera |
| P04 `sparse` | V=128,512,2048 | Cadena + hasta 4 destinos aleatorios por vértice | Caso disperso, alcanzable y con mejoras | Mejora creciente al subir V |
| P05 `grid` | V=144,529,2025 | Grilla cuadrada bidireccional | Red con grado bajo y múltiples rutas | Ventaja del heap con frontera acotada |
| P06 `disconnected` | V=128,512,2048 | Solo el primer 10% (redondeo hacia abajo) tiene aristas | Fracción alcanzable reducida | Heap evita búsquedas sobre inaccesibles; ambos inicializan todos los vértices |
| P07 `isolated` | V=128,512,2048 | E=0 | Ninguna relajación | Predominan inicialización y costos constantes; no esperar comportamiento cuadrático |
| P08 `dense` | V=64,128,256 | Completo dirigido; pesos 1..1000 | E=V(V−1), muchas aristas | Recorrer aristas reduce el beneficio relativo del heap |
| P09 `ties` | V=64,128,256 | Completo dirigido; todos los pesos 1 | Densidad sin mejoras repetidas | Densidad sola no basta para predecir el ganador |
| P10 `zero` | V=128,512,2048 | Disperso con aristas aleatorias de peso 0 y cadena positiva | Empates y ciclos de costo cero | Correctitud y ventaja en redes dispersas |
| P11 `adversarial` | V=32,64,128,256 | k=⌊(V−1)/2⌋ intermediarios, resto destinos | Muchas mejoras por destino antes de extraerlo | Heap acumula Θ(E) entradas y puede perder tiempo y memoria |
| P12 `parallel` | **V=2**, E=128,2048,16384 | Aristas 0→1, pesos E,E−1,…,1 | Multigrafo, orden adverso de adyacencia | Cada arista agrega una entrada al heap; el clásico puede ganar ampliamente |

P11: aristas 0→u de peso u, para u=1..k; u→t de peso 3k−2u.
Todos los intermediarios se procesan antes que cualquier destino. El candidato
para cada destino disminuye de 3k−1 a 2k; no hay pesos negativos.
P12 es deliberadamente un multigrafo, admitido por ambas representaciones:
no debe presentarse como un grafo simple ni como un caso típico de red vial.

38 configuraciones × semillas 17,43,91 × 7 rondas × 2 algoritmos = **1.596
muestras de lote por lenguaje**. Cada muestra contiene tantas ejecuciones como
determine la calibración; no equivale a una sola llamada. En familias
deterministas las semillas repiten el mismo grafo: no son tres grafos distintos.
Los tamaños finales pueden ser poco representativos de producción; la matriz
busca aislar mecanismos, no simular una aplicación concreta.

## Correctitud y bordes

| ID | Verificación | Criterio |
|---|---|---|
| C01 | Un vértice, origen=destino | Distancia 0 y camino de un vértice |
| C02 | Vértices inaccesibles | Infinito, sin predecesor, camino vacío |
| C03 | Autoaristas, ciclos y pesos cero | Termina, sin ciclos en los predecesores |
| C04 | Ruta indirecta más corta / entrada obsoleta | Se descarta la distancia vieja; resultado óptimo |
| C05 | Aristas paralelas | Se obtiene el menor costo disponible |
| C06 | Empates | Se comparan costos y validez del camino, no identidad del predecesor |
| C07 | Pesos enteros grandes y fraccionarios, Python | Coincide con el oráculo |
| C08 | 100 grafos pequeños aleatorios por implementación de lenguaje | Coincide con Bellman-Ford; cada camino tiene el costo informado |
| C09 | Cada familia de la matriz, tamaño menor, Python | Funciones reales y contadores coinciden con Bellman-Ford |
| C10 | Todos los grafos de rendimiento | Igualdad de distancias normal/heap antes de medir |
| C11 | Misma bolsa de aristas paralelas en orden ascendente y descendente | Mismas distancias; el contador demuestra que cambia el trabajo del heap |
| L01 | Python: etiquetas int y str con empate | Limitación conocida: `heapq` compara etiquetas y lanza TypeError |
| L02 | Java: camino de costo 4.000.000.000 | Limitación conocida: desbordamiento de int |
| L03 | Java: distancia exactamente Integer.MAX_VALUE | Limitación conocida: se confunde con infinito y no hay camino |

L01–L03 son `xfail(strict=True)`: prueban límites conocidos que siguen presentes,
no son casos correctos ni errores ocultos. Si se corrigen, la suite exige actualizar
las expectativas (un XPASS estricto falla). El harness Java verifica 102 grafos
en ambas variantes y los caminos de todos sus vértices.

## Dominio y exclusiones

- Pesos finitos, no negativos; origen existente, destinos declarados en el grafo.
  Un grafo vacío sin origen no define esta consulta. Las funciones actuales no
  validan estas precondiciones; no usar NaN, infinito o pesos negativos.
- No se ejecutan ciclos negativos: Dijkstra no es un algoritmo para ese dominio
  y la implementación con heap podría no terminar.
- Python en rendimiento: etiquetas enteras homogéneas. Para soportar etiquetas
  arbitrarias en el heap hace falta un desempate independiente de la etiqueta.
- Java en rendimiento: pesos/candidatos pequeños, lejos del límite de int.
  Mantener solo la distancia mínima final por debajo del límite no basta:
  **también deben entrar en rango todas las sumas candidatas evaluadas**.
- No se miden construcción, generación, lectura de archivos, compilación,
  impresión, reconstrucción de caminos ni instrumentación dentro del tiempo.
  Sí se incluyen inicialización, asignaciones y creación del resultado.
- No se compara con matrices de adyacencia, Fibonacci heap, BFS, A* ni lenguajes.
  Una tercera variante puede ser útil después, pero responde otra pregunta.

## Métricas y reglas de lectura

Tiempo: mediana de ms por llamada completa, obtenida de lotes calibrados a ≥5 ms
(o hasta el tope de 262.144 llamadas). Tres lotes adicionales de calentamiento,
siete rondas con orden aleatorio por grafo. Se aleatoriza también el orden de los
grafos. Se guardan todas las muestras, sin eliminar valores atípicos.

Ganancia = tiempo normal / tiempo heap por pareja (grafo y ronda). Se informa
la mediana de esos cocientes y P25–P75 descriptivos; **no son intervalos de
confianza** ni una prueba de significancia. Una mediana de cocientes puede no
coincidir con el cociente de las dos medianas de tiempo.

Python: GC cíclico desactivado durante las mediciones de ambas variantes;
conteo de referencias activo. Pico de memoria en una ejecución separada por
grafo y algoritmo con `tracemalloc`, excluyendo el grafo previamente creado e
incluyendo resultado y espacio auxiliar. No equivale a RSS ni a memoria Java.

Contadores Python en réplicas instrumentadas, verificados contra las funciones
reales: selecciones lineales (`scans`), aristas examinadas (`edges`), mejoras,
push/pop, extracciones obsoletas y pico de entradas de cola. No cuentan ciclos
de CPU ni todas las comparaciones internas de heapq.

Java: `System.nanoTime`, lotes, calentamiento, uso del resultado mediante un
campo `volatile`, una JVM, heap de 256 MiB a 1 GiB y GC habilitado. El harness es
**exploratorio, no JMH**: JIT, GC y orden de ejecución pueden influir. No hay
múltiples forks/JVM independientes ni conclusiones estadísticas universales.
No se mide memoria ni se atribuyen contadores Java a partir de Python.

No hay aserciones de velocidad en CI: dependen del equipo y generan pruebas
inestables. Correctitud sí es obligatoria. Confirmar diferencias cercanas a 1×
con ejecuciones independientes antes de sostenerlas en la charla.
