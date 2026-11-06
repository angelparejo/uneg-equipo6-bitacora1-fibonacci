"""Dos algoritmos para el n-ésimo número de Fibonacci.

Especificación
--------------
Precondición: n es un entero >= 0. True y False no se aceptan, aunque en
Python bool sea subclase de int.
Postcondición: el resultado es F(n), definido por
    F(0) = 0,  F(1) = 1,  F(n) = F(n - 1) + F(n - 2) para n >= 2.
"""


def validar_n(n):
    """Exige la precondición de ambas funciones."""
    if isinstance(n, bool) or not isinstance(n, int) or n < 0:
        raise ValueError(
            "La precondición exige un entero n >= 0. "
            "No se aceptan negativos, reales, textos ni booleanos."
        )


def fibonacci_ingenuo(n):
    """Recurrencia directa. Cada llamada resuelve otra vez los subproblemas.

    Correcto por inducción: los casos n = 0 y n = 1 devuelven la definición,
    y si las llamadas con argumento menor son correctas, la suma es F(n).
    El argumento decrece, así que la recursión termina.
    """
    validar_n(n)
    if n == 0:
        return 0
    if n == 1:
        return 1
    return fibonacci_ingenuo(n - 1) + fibonacci_ingenuo(n - 2)


def fibonacci_iterativo(n):
    """Versión con dos variables.

    Invariante de ciclo. Justo antes de ejecutar la iteración i
    (i toma los valores 2, 3, ..., n):
        a = F(i - 2)  y  b = F(i - 1).
    Al salir del ciclo, b = F(n).

    Inicialización: a = F(0) y b = F(1), que es el invariante para i = 2.
    Mantenimiento: a' = b = F(i - 1) y b' = a + b = F(i - 2) + F(i - 1) = F(i),
    que es el invariante para i + 1.
    Terminación: el rango 2..n es finito. En la última vuelta i = n deja b = F(n).
    """
    validar_n(n)
    if n == 0:
        return 0
    if n == 1:
        return 1

    a, b = 0, 1
    for i in range(2, n + 1):
        # Al entrar: a == F(i - 2) y b == F(i - 1).
        a, b = b, a + b
    return b
