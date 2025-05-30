import numpy as np

def gauss_jordan_logica(matriz_aumentada):
    matriz = matriz_aumentada.astype(float)
    n = matriz.shape[0]

    for i in range(n):
        # Buscar pivote máximo en la columna i
        max_row = i + np.argmax(abs(matriz[i:, i]))
        if abs(matriz[max_row, i]) < 1e-12:
            return None, "El sistema no tiene solución única (pivote nulo)."

        if max_row != i:
            matriz[[i, max_row]] = matriz[[max_row, i]]

        matriz[i] = matriz[i] / matriz[i, i]

        for j in range(n):
            if j != i:
                matriz[j] = matriz[j] - matriz[j, i] * matriz[i]

    soluciones = matriz[:, -1]

    return soluciones, None

def parse_matriz(texto):
    """
    Convierte texto multilinea a np.array
    """
    try:
        filas = texto.strip().split("\n")
        matriz = []
        for fila in filas:
            valores = fila.strip().split()
            matriz.append([float(v) for v in valores])
        return np.array(matriz)
    except:
        return None
