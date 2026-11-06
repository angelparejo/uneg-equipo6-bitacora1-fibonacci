"""Pruebas de precondición, casos conocidos, invariante y contraste diferencial."""

import unittest

from fibonacci import fibonacci_ingenuo, fibonacci_iterativo

# Primeros valores de la definición. Sirven de oráculo independiente del ciclo.
ESPERADOS = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987]


class PruebasFibonacci(unittest.TestCase):
    def test_casos_conocidos_iterativo(self):
        for n, esperado in enumerate(ESPERADOS):
            self.assertEqual(fibonacci_iterativo(n), esperado)

    def test_casos_conocidos_ingenuo(self):
        for n, esperado in enumerate(ESPERADOS):
            self.assertEqual(fibonacci_ingenuo(n), esperado)

    def test_precondicion_en_ambas(self):
        entradas_invalidas = [-1, -5, 1.5, "5", 3.0, True, False]
        for entrada in entradas_invalidas:
            with self.subTest(entrada=entrada):
                with self.assertRaises(ValueError):
                    fibonacci_iterativo(entrada)
                with self.assertRaises(ValueError):
                    fibonacci_ingenuo(entrada)

    def test_contraste_diferencial(self):
        for n in range(0, 21):
            with self.subTest(n=n):
                self.assertEqual(fibonacci_ingenuo(n), fibonacci_iterativo(n))

    def test_valores_grandes_conocidos(self):
        """Comprueba la función real, no una copia del ciclo, con valores publicados (OEIS A000045)."""
        conocidos = {
            50: 12586269025,
            100: 354224848179261915075,
            200: 280571172992510140037611932413038677189525,
        }
        for n, esperado in conocidos.items():
            with self.subTest(n=n):
                self.assertEqual(fibonacci_iterativo(n), esperado)
        self.assertEqual(fibonacci_ingenuo(25), 75025)

    def test_invariante_del_ciclo(self):
        """Reconstruye F con la recurrencia y revisa el invariante en cada vuelta."""
        n = 30
        fib = [0, 1]
        for k in range(2, n + 1):
            fib.append(fib[-1] + fib[-2])

        a, b = 0, 1
        for i in range(2, n + 1):
            self.assertEqual(a, fib[i - 2], f"a falló al entrar a i={i}")
            self.assertEqual(b, fib[i - 1], f"b falló al entrar a i={i}")
            a, b = b, a + b

        self.assertEqual(b, fib[n])
        self.assertEqual(b, fibonacci_iterativo(n))


if __name__ == "__main__":
    unittest.main(verbosity=2)
