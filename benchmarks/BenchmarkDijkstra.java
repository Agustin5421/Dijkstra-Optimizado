import adt.GrafoADT;
import algoritmos.Dijkstra;
import algoritmos.DijkstraNormal;
import algoritmos.ResultadoDijkstra;
import impl.GrafoListaAdyacencia;
import java.io.*;
import java.nio.file.*;
import java.util.*;

/** Harness exploratorio de una JVM; no compara lenguajes ni reemplaza JMH. */
public class BenchmarkDijkstra {
    private static volatile int sink;

    private static ResultadoDijkstra run(GrafoADT graph, boolean heap) {
        ResultadoDijkstra result;
        if (heap) {
            result = Dijkstra.dijkstra(graph, 0);
        } else {
            result = DijkstraNormal.dijkstra(graph, 0);
        }
        return result;
    }

    private static long batch(GrafoADT graph, boolean heap, int count) {
        long start = System.nanoTime();
        for (int i = 0; i < count; i++) {
            ResultadoDijkstra result = run(graph, heap);
            sink = result.distancia(graph.cantidadVertices() - 1);
        }
        return System.nanoTime() - start;
    }

    public static void main(String[] args) throws Exception {
        Path root = Path.of(args[0]);
        int repetitions = Integer.parseInt(args[2]);
        Random order = new Random(20261020);
        try (PrintWriter out = new PrintWriter(args[1])) {
            out.println("family,size,seed,rep,algorithm,ns_per_call,batch");
            List<String> cases = Files.readAllLines(root.resolve("manifest.csv"));
            Collections.shuffle(cases, order);
            for (String line : cases) {
                String[] fields = line.split(",");
                GrafoADT graph;
                try (Scanner input = new Scanner(root.resolve(fields[3]))) {
                    graph = new GrafoListaAdyacencia(input.nextInt());
                    int edges = input.nextInt();
                    for (int e = 0; e < edges; e++) {
                        graph.agregarArista(input.nextInt(), input.nextInt(), input.nextInt());
                    }
                }
                ResultadoDijkstra classic = run(graph, false);
                ResultadoDijkstra optimized = run(graph, true);
                for (int v = 0; v < graph.cantidadVertices(); v++) {
                    if (classic.distancia(v) != optimized.distancia(v)) {
                        throw new AssertionError("Diferencia en " + line + ", v=" + v);
                    }
                }
                int[] counts = new int[2];
                for (int a = 0; a < 2; a++) {
                    int count = 1;
                    long elapsed = batch(graph, a == 1, count);
                    while (elapsed < 5_000_000 && count < 262144) {
                        count *= 2;
                        elapsed = batch(graph, a == 1, count);
                    }
                    counts[a] = count;
                    for (int w = 0; w < 3; w++) {
                        batch(graph, a == 1, count);
                    }
                }
                for (int rep = 0; rep < repetitions; rep++) {
                    boolean heapFirst = order.nextBoolean();
                    for (int pos = 0; pos < 2; pos++) {
                        boolean heap = pos == 0 ? heapFirst : heapFirst == false;
                        int count = counts[heap ? 1 : 0];
                        double ns = (double) batch(graph, heap, count) / count;
                        out.printf(Locale.ROOT, "%s,%s,%s,%d,%s,%.3f,%d%n",
                                fields[0], fields[1], fields[2], rep,
                                heap ? "heap" : "normal", ns, count);
                    }
                }
                out.flush();
                System.out.println("Java: " + fields[0] + " " + fields[1] + " seed=" + fields[2]);
            }
        }
    }
}
