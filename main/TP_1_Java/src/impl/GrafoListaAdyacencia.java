package impl;

import adt.Arista;
import adt.GrafoADT;

/**
 * Grafo con listas de adyacencia enlazadas: una lista por vértice.
 */
public class GrafoListaAdyacencia implements GrafoADT {

    private static class Nodo {
        Arista arista;
        Nodo siguiente;

        Nodo(Arista arista, Nodo siguiente) {
            this.arista = arista;
            this.siguiente = siguiente;
        }
    }

    private final Nodo[] listas;
    private final int[] grados;

    public GrafoListaAdyacencia(int cantidadVertices) {
        listas = new Nodo[cantidadVertices];
        grados = new int[cantidadVertices];
    }

    @Override
    public int cantidadVertices() {
        return listas.length;
    }

    @Override
    public void agregarArista(int origen, int destino, int peso) {
        // Se inserta al principio: O(1)
        listas[origen] = new Nodo(new Arista(destino, peso), listas[origen]);
        grados[origen]++;
    }

    @Override
    public Arista[] adyacentes(int v) {
        Arista[] resultado = new Arista[grados[v]];
        int i = 0;
        for (Nodo n = listas[v]; n != null; n = n.siguiente) {
            resultado[i++] = n.arista;
        }
        return resultado;
    }
}
