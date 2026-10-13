package adt;

public class Arista {

    private final int destino;
    private final int peso;

    public Arista(int destino, int peso) {
        this.destino = destino;
        this.peso = peso;
    }

    public int getDestino() {
        return destino;
    }

    public int getPeso() {
        return peso;
    }
}
