package adt;

/**
 * Grafo dirigido y ponderado con vértices 0..n-1.
 * Para un grafo no dirigido se agrega la arista en ambos sentidos.
 */
public interface GrafoADT {

    /** Cantidad de vértices del grafo. */
    int cantidadVertices();

    /**
     * Agrega la arista origen -> destino con el peso indicado.
     * Precondición: origen y destino válidos, peso >= 0.
     */
    void agregarArista(int origen, int destino, int peso);

    /**
     * Devuelve las aristas salientes de v.
     * Precondición: v válido.
     */
    Arista[] adyacentes(int v);
}
