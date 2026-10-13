package impl;

import adt.ColaPrioridadADT;

/**
 * Cola de prioridad implementada con un min-heap binario sobre arrays.
 * acolar y desacolar: O(log n). primero y prioridadPrimero: O(1).
 */
public class ColaPrioridadHeap implements ColaPrioridadADT {

    private int[] elementos;
    private int[] prioridades;
    private int cantidad;

    public ColaPrioridadHeap() {
        elementos = new int[16];
        prioridades = new int[16];
        cantidad = 0;
    }

    @Override
    public void acolar(int elemento, int prioridad) {
        if (cantidad == elementos.length) {
            agrandar();
        }
        elementos[cantidad] = elemento;
        prioridades[cantidad] = prioridad;
        subir(cantidad);
        cantidad++;
    }

    @Override
    public void desacolar() {
        cantidad--;
        elementos[0] = elementos[cantidad];
        prioridades[0] = prioridades[cantidad];
        bajar(0);
    }

    @Override
    public int primero() {
        return elementos[0];
    }

    @Override
    public int prioridadPrimero() {
        return prioridades[0];
    }

    @Override
    public boolean estaVacia() {
        return cantidad == 0;
    }

    private void subir(int i) {
        while (i > 0) {
            int padre = (i - 1) / 2;
            if (prioridades[i] >= prioridades[padre]) {
                return;
            }
            intercambiar(i, padre);
            i = padre;
        }
    }

    private void bajar(int i) {
        while (true) {
            int izq = 2 * i + 1;
            int der = 2 * i + 2;
            int menor = i;

            if (izq < cantidad && prioridades[izq] < prioridades[menor]) {
                menor = izq;
            }
            if (der < cantidad && prioridades[der] < prioridades[menor]) {
                menor = der;
            }
            if (menor == i) {
                return;
            }
            intercambiar(i, menor);
            i = menor;
        }
    }

    private void intercambiar(int i, int j) {
        int e = elementos[i];
        elementos[i] = elementos[j];
        elementos[j] = e;

        int p = prioridades[i];
        prioridades[i] = prioridades[j];
        prioridades[j] = p;
    }

    private void agrandar() {
        int[] nuevosElementos = new int[elementos.length * 2];
        int[] nuevasPrioridades = new int[prioridades.length * 2];
        for (int i = 0; i < cantidad; i++) {
            nuevosElementos[i] = elementos[i];
            nuevasPrioridades[i] = prioridades[i];
        }
        elementos = nuevosElementos;
        prioridades = nuevasPrioridades;
    }
}
