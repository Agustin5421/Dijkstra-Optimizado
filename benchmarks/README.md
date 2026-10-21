# Comparación de Dijkstra: TP1

Entregables:

- [Informe y conclusiones](INFORME.md), con números obtenidos en esta ejecución.
- [Matriz y metodología](MATRIZ.md), con hipótesis, casos borde y límites.
- [Resultados originales](results/): CSV por muestra, resúmenes, contadores,
  memoria, entorno y gráficos PNG/SVG.
- [Guion para la charla](CHARLA.md).

## Ejecutar

Desde la raíz, con Python 3.11+ y JDK 17+ para Java:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r benchmarks/requirements.txt
.venv/bin/python -m pytest -q -ra
.venv/bin/python benchmarks/run.py --java
```

Solo rendimiento Python: omitir `--java`. Prueba rápida sin sobrescribir el
experimento completo:

```sh
.venv/bin/python benchmarks/run.py --java --quick
```

Usar `--output /ruta/a/resultados` para conservar ejecuciones independientes.
El comando escribe gráficos y datos; el informe y el guion son una interpretación
de la ejecución guardada, **no se regeneran automáticamente** al volver a medir.
Actualizar sus conclusiones si cambian los resultados. Los hashes de fuentes
y versiones se guardan en `environment.json`; el commit es el de partida y los
archivos nuevos se identifican por SHA-256.

La ejecución completa realiza 114 instancias por lenguaje. Puede tardar varios
minutos. Cerrar otras tareas intensivas y evitar medir simultáneamente con tests.
No se necesita acceso a red para correrla después de instalar dependencias.
Matplotlib usa el backend Agg, sin abrir ventanas.

## Qué hay en las carpetas

`main/TP_1`: versión Python original con `heapq`, diccionarios y listas de
adyacencia. `main.py` es una demo, y `dijkstra_visual.html` una visualización;
no son pruebas de rendimiento. `dijkstra_normal.py` agrega la referencia clásica.

`main/TP_1_Java`: adaptación del mismo algoritmo con ADT propios: heap binario
en arrays y adyacencia en listas enlazadas. `adyacentes()` materializa un array
nuevo por consulta; ambas variantes Java pagan ese costo. `DijkstraNormal.java`
agrega la referencia clásica con los mismos tipos y representación.

Las implementaciones con heap originales se conservan para evaluar exactamente
lo que había en el repositorio. Los límites encontrados se exponen con pruebas
de fallo esperado; no se mezclan cambios de algoritmo con la medición inicial.

## Datos guardados

| Archivo | Contenido |
|---|---|
| `python_raw.csv`, `java_raw.csv` | Familia, tamaño, semilla, ronda, algoritmo, ns/llamada, llamadas/lote |
| `*_summary.csv` | Medianas de tiempo, ganancia y P25/P75 por configuración |
| `operations_memory.csv` | Contadores y pico de bytes Python por grafo y algoritmo |
| `summary.json` | Mismos resúmenes para consumo automático |
| `environment.json` | Versiones, plataforma, parámetros, commit y hashes de fuentes |
| `*_escenarios.png/.svg` | Ganancia por familia en el mayor tamaño |
| `*_tiempos.png/.svg` | Dos barras por escenario: optimizado arriba y sin optimizar abajo; tiempos en ms, escala lineal propia por panel |
| `*_escalado.png/.svg` | Curvas por familia |
| `python_memoria.png/.svg` | Pico auxiliar + resultado, sin el grafo |

Las curvas de Python y Java se interpretan por separado. No usar estos archivos
para atribuir diferencias entre lenguajes.
