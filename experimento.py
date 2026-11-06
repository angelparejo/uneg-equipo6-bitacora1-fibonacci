"""Experimento de duplicación: mediana de tiempos y razón T(2n)/T(n).

La semilla queda registrada porque la guía lo pide. El cronómetro no usa
números aleatorios; la semilla no cambia las mediciones y se escribe en
los metadatos para dejar constancia de eso.
"""

import csv
import platform
import random
import statistics
import sys
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from fibonacci import fibonacci_ingenuo, fibonacci_iterativo

SEMILLA = 20261106
REPETICIONES = 5
TAMANIOS_ITERATIVO = [10_000, 20_000, 40_000, 80_000, 160_000, 320_000]
TAMANIOS_INGENUO = [8, 10, 12, 14, 16, 20, 24, 28, 32]

RAIZ = Path(__file__).resolve().parent
DIR_DATOS = RAIZ / "datos"
DIR_FIGURAS = RAIZ / "figuras"


def medir_mediana(funcion, n, repeticiones):
    """Una llamada de calentamiento y luego la mediana de `repeticiones`."""
    funcion(n)
    tiempos = []
    for _ in range(repeticiones):
        inicio = time.perf_counter()
        funcion(n)
        tiempos.append(time.perf_counter() - inicio)
    return statistics.median(tiempos), min(tiempos), max(tiempos)


def razon_si_hay_mitad(filas, n, tiempo):
    """T(n) / T(n/2) cuando n/2 también fue medido. Esa es T(2m)/T(m) con m = n/2."""
    mitad = n / 2
    for fila in filas:
        if fila["n"] == mitad:
            base = fila["mediana_s"]
            if base <= 0:
                return None
            return tiempo / base
    return None


def correr_serie(funcion, tamanios, repeticiones, etiqueta):
    filas = []
    for n in tamanios:
        print(f"  {etiqueta}: n={n} ({repeticiones} repeticiones)...", flush=True)
        mediana, minimo, maximo = medir_mediana(funcion, n, repeticiones)
        razon = razon_si_hay_mitad(filas, n, mediana)
        filas.append(
            {
                "n": n,
                "mediana_s": mediana,
                "minimo_s": minimo,
                "maximo_s": maximo,
                "razon_t2n_tn": razon,
            }
        )
        texto_razon = "N/A" if razon is None else f"{razon:.2f}"
        print(f"    mediana={mediana:.6e} s   T(2n)/T(n)={texto_razon}", flush=True)
    return filas


def guardar_csv(ruta, filas):
    with ruta.open("w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(
            archivo,
            fieldnames=["n", "mediana_s", "minimo_s", "maximo_s", "razon_t2n_tn"],
        )
        escritor.writeheader()
        for fila in filas:
            escritor.writerow(
                {
                    "n": fila["n"],
                    "mediana_s": f"{fila['mediana_s']:.10e}",
                    "minimo_s": f"{fila['minimo_s']:.10e}",
                    "maximo_s": f"{fila['maximo_s']:.10e}",
                    "razon_t2n_tn": ""
                    if fila["razon_t2n_tn"] is None
                    else f"{fila['razon_t2n_tn']:.10f}",
                }
            )


def guardar_metadatos(ruta):
    lineas = [
        f"semilla={SEMILLA}",
        "aleatoriedad=ninguna",
        "nota=El experimento cronometra funciones deterministas. La semilla se fija y se registra; no interviene en los tiempos.",
        f"python={sys.version.replace(chr(10), ' ')}",
        f"plataforma={platform.platform()}",
        f"repeticiones={REPETICIONES}",
        "calentamiento=1 llamada por cada n, fuera de la mediana",
        "reloj=time.perf_counter",
        "estadistico=mediana",
        f"tamanios_iterativo={TAMANIOS_ITERATIVO}",
        f"tamanios_ingenuo={TAMANIOS_INGENUO}",
        "modelo_de_duplicacion=la razón de una fila es T(n)/T(n/2) cuando n/2 está en la serie",
    ]
    ruta.write_text("\n".join(lineas) + "\n", encoding="utf-8")


def _graficar(filas, titulo_tiempo, titulo_razon, ruta, referencias):
    ns = [fila["n"] for fila in filas]
    tiempos = [fila["mediana_s"] for fila in filas]
    puntos_razon = [
        (fila["n"], fila["razon_t2n_tn"])
        for fila in filas
        if fila["razon_t2n_tn"] is not None
    ]

    figura, ejes = plt.subplots(1, 2, figsize=(10.4, 4.3))

    ejes[0].plot(ns, tiempos, marker="o", color="#1f4e79", linewidth=1.8)
    ejes[0].set_xlabel("n")
    ejes[0].set_ylabel("Tiempo mediano (s)")
    ejes[0].set_title(titulo_tiempo)
    ejes[0].grid(True, alpha=0.3)
    if max(tiempos) / max(min(tiempos), 1e-12) > 50:
        ejes[0].set_yscale("log")
        ejes[0].set_ylabel("Tiempo mediano (s, escala log)")

    if puntos_razon:
        ejes[1].plot(
            [n for n, _ in puntos_razon],
            [r for _, r in puntos_razon],
            marker="o",
            color="#c45911",
            linewidth=1.8,
            label="Medición",
        )
    for valor, texto, estilo in referencias:
        ejes[1].axhline(valor, color="#5b5b5b", linestyle=estilo, linewidth=1, label=texto)
    ejes[1].set_xlabel("n (tamaño mayor de cada pareja)")
    ejes[1].set_ylabel("T(2n) / T(n)")
    ejes[1].set_title(titulo_razon)
    ejes[1].grid(True, alpha=0.3)
    if puntos_razon and (max(r for _, r in puntos_razon) / min(r for _, r in puntos_razon) > 20):
        ejes[1].set_yscale("log")
        ejes[1].set_ylabel("T(2n) / T(n), escala log")
    if puntos_razon or referencias:
        ejes[1].legend(fontsize=8)

    figura.tight_layout()
    figura.savefig(ruta, dpi=150)
    plt.close(figura)


def graficar(filas_iterativo, filas_ingenuo):
    _graficar(
        filas_iterativo,
        "Fibonacci iterativo: tiempo mediano",
        "Razón T(2n)/T(n) del iterativo",
        DIR_FIGURAS / "iterativo_tiempo_y_razon.png",
        [
            (2, "Referencia lineal (2)", "--"),
            (4, "Referencia cuadrática (4)", ":"),
        ],
    )
    _graficar(
        filas_ingenuo,
        "Fibonacci ingenuo: tiempo mediano",
        "Razón T(2n)/T(n) del ingenuo",
        DIR_FIGURAS / "ingenuo_tiempo_y_razon.png",
        [],
    )


def main():
    random.seed(SEMILLA)
    DIR_DATOS.mkdir(exist_ok=True)
    DIR_FIGURAS.mkdir(exist_ok=True)

    print("=== Serie iterativa ===", flush=True)
    filas_iterativo = correr_serie(
        fibonacci_iterativo, TAMANIOS_ITERATIVO, REPETICIONES, "iterativo"
    )
    print("=== Serie ingenua ===", flush=True)
    filas_ingenuo = correr_serie(
        fibonacci_ingenuo, TAMANIOS_INGENUO, REPETICIONES, "ingenuo"
    )

    guardar_csv(DIR_DATOS / "iterativo.csv", filas_iterativo)
    guardar_csv(DIR_DATOS / "ingenuo.csv", filas_ingenuo)
    guardar_metadatos(DIR_DATOS / "metadatos.txt")
    graficar(filas_iterativo, filas_ingenuo)
    print("Datos en datos/ y gráficas en figuras/.", flush=True)


if __name__ == "__main__":
    main()
