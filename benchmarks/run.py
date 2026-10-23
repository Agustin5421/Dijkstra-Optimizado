"""Ejecutar desde cualquier carpeta: python benchmarks/run.py --java."""
import argparse
import csv
from datetime import datetime, timezone
import gc
import hashlib
import json
import os
from pathlib import Path
import platform
import random
import statistics
import subprocess
import sys
import tempfile
import time
import tracemalloc

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "main/TP_1"))
from dijkstra_normal import dijkstra as normal
from dijkstra_pq import dijkstra as heap
from metrics import count_operations
from scenarios import LABELS, SIZES, make_graph


def write_csv(path, rows):
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def timed_batch(algorithm, graph, count):
    start = time.perf_counter_ns()
    for _ in range(count):
        result = algorithm(graph, 0)
    elapsed = time.perf_counter_ns() - start
    # Usar el resultado fuera del reloj; las funciones reales se miden completas.
    assert result[0][0] == 0
    return elapsed


def calibrate(algorithm, graph):
    count = 1
    elapsed = timed_batch(algorithm, graph, count)
    while elapsed < 5_000_000 and count < 262144:
        count *= 2
        elapsed = timed_batch(algorithm, graph, count)
    for _ in range(3):
        timed_batch(algorithm, graph, count)
    return count


def peak_memory(algorithm, graph):
    gc.collect()
    tracemalloc.start()
    result = algorithm(graph, 0)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    assert result[0][0] == 0
    return peak


def summarize(raw):
    groups = {}
    for row in raw:
        key = (row["family"], int(row["size"]))
        groups.setdefault(key, []).append(row)
    summary = []
    for (family, size), rows in groups.items():
        pairs = {}
        times = {"normal": [], "heap": []}
        for row in rows:
            ns = float(row["ns_per_call"])
            times[row["algorithm"]].append(ns)
            pairs.setdefault((int(row["seed"]), int(row["rep"])), {})[row["algorithm"]] = ns
        ratios = [pair["normal"] / pair["heap"] for pair in pairs.values()]
        q1, _, q3 = statistics.quantiles(ratios, n=4, method="inclusive")
        summary.append(dict(family=family, size=size, normal_ms=statistics.median(times["normal"]) / 1e6,
                            heap_ms=statistics.median(times["heap"]) / 1e6,
                            speedup=statistics.median(ratios), ratio_q1=q1, ratio_q3=q3,
                            pairs=len(pairs)))
    return sorted(summary, key=lambda row: (list(SIZES).index(row["family"]), row["size"]))


def plot_results(output, language, summary):
    # Cache y backend locales para entornos sin escritorio.
    os.environ.setdefault("MPLCONFIGDIR", str(output / ".matplotlib"))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import NullLocator, NullFormatter
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "axes.spines.top": False, "axes.spines.right": False})
    selected = [max((r for r in summary if r["family"] == f), key=lambda r: r["size"])
                for f in SIZES if any(r["family"] == f for r in summary)]
    fig, ax = plt.subplots(figsize=(12, 7))
    ys = list(range(len(selected)))
    ratios = [r["speedup"] for r in selected]
    ax.barh(ys, ratios, color=["#178375" if x > 1 else "#cf6247" for x in ratios])
    ax.axvline(1, color="#222222", linestyle="--")
    ax.set_xscale("log")
    ax.set_yticks(ys, [f'{LABELS[r["family"]]} ({"E" if r["family"] == "parallel" else "V"}={r["size"]})'
                      for r in selected])
    for y, row in zip(ys, selected):
        ax.plot([row["ratio_q1"], row["ratio_q3"]], [y, y], color="#222222", linewidth=2)
        ax.annotate(f'{row["speedup"]:.2f}×', (row["speedup"], y), xytext=(7, 0),
                    textcoords="offset points", va="center")
    ax.set_xlim(min(0.1, min(ratios) / 2), max(ratios) * 2.5)
    ax.invert_yaxis()
    ax.set_xlabel("Tiempo normal / tiempo heap (escala log). >1: gana heap; <1: gana normal")
    ax.set_title(f"{language}: ganancia por escenario, mayor tamaño ensayado\n"
                 "Mediana de cocientes pareados; segmentos: percentiles 25–75, sin IC")
    fig.tight_layout()
    fig.savefig(output / f"{language.lower()}_escenarios.png", dpi=180)
    fig.savefig(output / f"{language.lower()}_escenarios.svg")
    plt.close(fig)

    fig, axes = plt.subplots(3, 4, figsize=(16, 11))
    for ax, family in zip(axes.flat, SIZES):
        rows = [r for r in summary if r["family"] == family]
        for algorithm, color in (("normal", "#526981"), ("heap", "#178375")):
            ax.plot([r["size"] for r in rows], [r[f"{algorithm}_ms"] for r in rows],
                    marker="o", label=algorithm, color=color)
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xticks([r["size"] for r in rows], [str(r["size"]) for r in rows])
        ax.xaxis.set_minor_locator(NullLocator())
        ax.yaxis.set_minor_formatter(NullFormatter())
        ax.set_title(LABELS[family])
        ax.set_xlabel("E (V=2)" if family == "parallel" else "Vértices")
        ax.set_ylabel("Milisegundos (mediana)")
        ax.grid(alpha=0.2)
    axes.flat[0].legend()
    fig.suptitle(f"{language}: crecimiento dentro de cada escenario · ejes logarítmicos", fontsize=16)
    fig.tight_layout(rect=(0, 0, 1, 0.96), h_pad=2.5, w_pad=2)
    fig.savefig(output / f"{language.lower()}_escalado.png", dpi=180)
    fig.savefig(output / f"{language.lower()}_escalado.svg")
    plt.close(fig)


def plot_absolute_times(output, language, summary):
    """Dos barras por escenario; escalas lineales independientes y tiempos reales."""
    os.environ.setdefault("MPLCONFIGDIR", str(output / ".matplotlib"))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MaxNLocator

    fig, axes = plt.subplots(3, 4, figsize=(20, 11))
    for ax, family in zip(axes.flat, SIZES):
        row = max((r for r in summary if r["family"] == family), key=lambda r: r["size"])
        values = [row["heap_ms"], row["normal_ms"]]
        ax.barh([0, 1], values, height=0.48, color=["#178375", "#526981"])
        ax.set_yticks([0, 1], ["Optimizado", "Sin optimizar"], fontsize=10)
        ax.set_ylim(1.7, -0.7)
        maximum = max(values)
        ax.set_xlim(0, maximum * 1.52)
        for y, value in enumerate(values):
            # Mantener diferencias visibles también en los escenarios muy pequeños.
            label = f"{value:.3g} ms" if value < 0.01 else f"{value:.3f} ms"
            ax.text(value + maximum * 0.025, y, label, va="center", fontsize=10)
        size = f'E = {row["size"]:,}, V = 2' if family == "parallel" else f'V = {row["size"]:,}'
        ax.set_title(f"{LABELS[family]}\n{size}", fontsize=11, loc="left", pad=10)
        ax.set_xlabel("Tiempo (ms)", fontsize=9)
        ax.xaxis.set_major_locator(MaxNLocator(nbins=3, min_n_ticks=2))
        ax.tick_params(axis="x", labelsize=8)
        ax.ticklabel_format(axis="x", style="plain", useOffset=False)
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.tick_params(axis="y", length=0)
        ax.set_axisbelow(True)
        ax.grid(axis="x", alpha=0.18)
    fig.suptitle(f"{language}: Dijkstra optimizado vs. sin optimizar", fontsize=20, y=0.985)
    fig.text(0.5, 0.94, "Tiempo mediano por ejecución · Una barra más corta significa menos tiempo\n"
             "Mayor tamaño de cada escenario · Cada panel tiene su propia escala lineal",
             ha="center", va="top", fontsize=12, color="#444444")
    fig.tight_layout(rect=(0.01, 0.01, 0.99, 0.91), h_pad=3, w_pad=2.5)
    fig.savefig(output / f"{language.lower()}_tiempos.png", dpi=180)
    fig.savefig(output / f"{language.lower()}_tiempos.svg")
    plt.close(fig)


def plot_memory(output, metrics):
    import matplotlib.pyplot as plt
    selected = []
    for family in SIZES:
        rows = [r for r in metrics if r["family"] == family]
        largest = max(r["size"] for r in rows)
        group = [r for r in rows if r["size"] == largest]
        pair = {a: statistics.median(r["peak_bytes"] for r in group if r["algorithm"] == a)
                for a in ("normal", "heap")}
        selected.append((family, pair))
    fig, ax = plt.subplots(figsize=(12, 7))
    for offset, algorithm, color in ((-0.18, "normal", "#526981"), (0.18, "heap", "#178375")):
        ax.barh([i + offset for i in range(len(selected))],
                [pair[algorithm] / 1024 for _, pair in selected], height=0.36,
                label=algorithm, color=color)
    ax.set_xscale("log")
    ax.set_yticks(range(len(selected)), [LABELS[f] for f, _ in selected])
    ax.invert_yaxis()
    ax.set_xlabel("Pico de memoria auxiliar + resultado (KiB, tracemalloc). Grafo excluido")
    ax.set_title("Python: costo de memoria por escenario · mayor tamaño ensayado")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output / "python_memoria.png", dpi=180)
    fig.savefig(output / "python_memoria.svg")
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--java", action="store_true", help="Medir también normal vs heap dentro de Java")
    parser.add_argument("--quick", action="store_true", help="Smoke: un tamaño, una semilla, 3 repeticiones")
    parser.add_argument("--output", type=Path, default=ROOT / "benchmarks/results")
    args = parser.parse_args()
    output = args.output.resolve()
    if args.quick and output == ROOT / "benchmarks/results":
        output = ROOT / "benchmarks/results_quick"
    output.mkdir(parents=True, exist_ok=True)
    seeds = [17] if args.quick else [17, 43, 91]
    repetitions = 3 if args.quick else 7
    cases = [(f, n, s) for f, sizes in SIZES.items()
             for n in (sizes[:1] if args.quick else sizes) for s in seeds]
    rng = random.Random(20261020)
    rng.shuffle(cases)
    raw, metrics, manifest = [], [], []
    with tempfile.TemporaryDirectory(prefix="dijkstra-fixtures-") as temp:
        fixtures = Path(temp)
        for index, (family, size, seed) in enumerate(cases):
            graph = make_graph(family, size, seed)
            edges = sum(map(len, graph.values()))
            reference = normal(graph, 0)[0]
            assert reference == heap(graph, 0)[0], (family, size, seed)
            if args.java:
                filename = f"{index}.txt"
                with (fixtures / filename).open("w") as stream:
                    stream.write(f"{len(graph)} {edges}\n")
                    for u, adjacency in graph.items():
                        # Java inserta al principio: invertir para preservar el orden lógico.
                        for v, weight in reversed(adjacency):
                            stream.write(f"{u} {v} {weight}\n")
                manifest.append(f"{family},{size},{seed},{filename}")
            enabled = gc.isenabled()
            gc.disable()
            try:
                counts = {a: calibrate(fn, graph) for a, fn in (("normal", normal), ("heap", heap))}
                for rep in range(repetitions):
                    algorithms = [("normal", normal), ("heap", heap)]
                    rng.shuffle(algorithms)
                    for name, algorithm in algorithms:
                        elapsed = timed_batch(algorithm, graph, counts[name])
                        raw.append(dict(family=family, size=size, seed=seed, rep=rep,
                                        algorithm=name, ns_per_call=elapsed / counts[name], batch=counts[name]))
            finally:
                if enabled:
                    gc.enable()
            for name, algorithm in (("normal", normal), ("heap", heap)):
                counted, counters = count_operations(graph, name == "heap")
                assert counted == reference
                metrics.append(dict(family=family, size=size, seed=seed, algorithm=name,
                                    vertices=len(graph), adjacency_entries=edges,
                                    peak_bytes=peak_memory(algorithm, graph), **counters))
            print(f"Python: {family} {size} seed={seed}", flush=True)
        write_csv(output / "python_raw.csv", raw)
        write_csv(output / "operations_memory.csv", metrics)
        summaries = {"Python": summarize(raw)}
        if args.java:
            (fixtures / "manifest.csv").write_text("\n".join(manifest) + "\n")
            build = fixtures / "classes"
            build.mkdir()
            sources = list((ROOT / "main/TP_1_Java/src").rglob("*.java"))
            subprocess.run(["javac", "-d", str(build), *map(str, sources),
                            str(ROOT / "benchmarks/BenchmarkDijkstra.java")], check=True)
            java_raw = output / "java_raw.csv"
            subprocess.run(["java", "-Xms256m", "-Xmx1g", "-cp", str(build), "BenchmarkDijkstra",
                            str(fixtures), str(java_raw), str(repetitions)], check=True)
            with java_raw.open() as stream:
                summaries["Java"] = summarize(list(csv.DictReader(stream)))
    for language, summary in summaries.items():
        write_csv(output / f"{language.lower()}_summary.csv", summary)
        plot_results(output, language, summary)
        plot_absolute_times(output, language, summary)
    plot_memory(output, metrics)
    sources = [ROOT / "main/TP_1/dijkstra_pq.py", ROOT / "main/TP_1/dijkstra_normal.py",
               *sorted((ROOT / "main/TP_1_Java/src").rglob("*.java")),
               *sorted((ROOT / "benchmarks").glob("*.py")),
               *sorted((ROOT / "benchmarks").glob("*.java"))]
    metadata = dict(timestamp_utc=datetime.now(timezone.utc).isoformat(),
                    platform=platform.platform(), machine=platform.machine(),
                    python=sys.version, executable=sys.executable, seeds=seeds,
                    repetitions=repetitions, cases=len(cases), configurations=len(cases) // len(seeds),
                    timer="perf_counter_ns / System.nanoTime", target_batch_ms=5,
                    warmup_batches=3, python_gc="desactivado solo durante tiempos",
                    java_flags="-Xms256m -Xmx1g; una JVM; GC habilitado; sin JMH",
                    git_revision=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                    source_sha256={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                   for p in sources})
    if args.java:
        metadata["java_version"] = subprocess.run(["java", "-version"], capture_output=True, text=True).stderr
    (output / "environment.json").write_text(json.dumps(metadata, indent=2) + "\n")
    (output / "summary.json").write_text(json.dumps(summaries, indent=2) + "\n")
    print(f"Resultados y gráficos: {output}")


if __name__ == "__main__":
    main()
