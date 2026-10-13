package adt;

/**
 * Cola de prioridad de mínimos: sale primero el elemento con menor prioridad.
 * Admite elementos repetidos.
 */
public interface ColaPrioridadADT {

    void acolar(int elemento, int prioridad);

    /**
     * Elimina el elemento de menor prioridad.
     * Precondición: la cola no está vacía.
     */
    void desacolar();

    /**
     * Devuelve el elemento de menor prioridad.
     * Precondición: la cola no está vacía.
     */
    int primero();

    /**
     * Devuelve la prioridad del primero.
     * Precondición: la cola no está vacía.
     */
    int prioridadPrimero();

    boolean estaVacia();
}
