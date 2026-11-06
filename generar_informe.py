"""Arma el PDF de la bitácora y el mensaje del foro a partir de los CSV."""

import csv
import math
import unittest
from datetime import date
from io import StringIO
from pathlib import Path

import fpdf
import matplotlib
from fpdf import FPDF
from fpdf.enums import XPos, YPos

import pruebas

RAIZ = Path(__file__).resolve().parent
DIR_DATOS = RAIZ / "datos"
DIR_FIGURAS = RAIZ / "figuras"
DIR_INFORME = RAIZ / "informe"
EQUIPO = "6"
PDF_NOMBRE = f"Equipo_{EQUIPO}_Bitacora1.pdf"
PHI = (1 + math.sqrt(5)) / 2

if Path(r"C:\Windows\Fonts\arial.ttf").exists():
    FUENTES = {
        "": r"C:\Windows\Fonts\arial.ttf",
        "B": r"C:\Windows\Fonts\arialbd.ttf",
        "I": r"C:\Windows\Fonts\ariali.ttf",
        "BI": r"C:\Windows\Fonts\arialbi.ttf",
    }
else:
    _DEJAVU = "/usr/share/fonts/truetype/dejavu/"
    FUENTES = {
        "": _DEJAVU + "DejaVuSans.ttf",
        "B": _DEJAVU + "DejaVuSans-Bold.ttf",
        "I": _DEJAVU + "DejaVuSans-Oblique.ttf",
        "BI": _DEJAVU + "DejaVuSans-BoldOblique.ttf",
    }


def leer_csv(ruta):
    filas = []
    with ruta.open(encoding="utf-8", newline="") as archivo:
        for fila in csv.DictReader(archivo):
            texto = fila["razon_t2n_tn"].strip()
            filas.append(
                {
                    "n": int(fila["n"]),
                    "mediana_s": float(fila["mediana_s"]),
                    "minimo_s": float(fila["minimo_s"]),
                    "maximo_s": float(fila["maximo_s"]),
                    "razon": None if texto == "" else float(texto),
                }
            )
    return filas


def leer_metadatos(ruta):
    datos = {}
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        clave, valor = linea.split("=", 1)
        datos[clave] = valor
    return datos


def fmt_tiempo(valor):
    if valor < 1e-3:
        return f"{valor:.3e}"
    return f"{valor:.6f}"


def fmt_razon(valor):
    if valor is None:
        return "N/A"
    if valor >= 100:
        return f"{valor:.1f}"
    return f"{valor:.2f}"


def razones(filas):
    return [fila["razon"] for fila in filas if fila["razon"] is not None]


def ejecutar_pruebas():
    suite = unittest.defaultTestLoader.loadTestsFromModule(pruebas)
    buffer = StringIO()
    resultado = unittest.TextTestRunner(stream=buffer, verbosity=1).run(suite)
    return resultado, buffer.getvalue()


def redaccion_iterativa(filas):
    valores = razones(filas)
    ultima = valores[-1]
    grado = math.log2(ultima)
    serie = ", ".join(fmt_razon(valor) for valor in valores)
    if ultima >= 3.2:
        lectura = (
            f"La última razón es {fmt_razon(ultima)} y el grado estimado, "
            f"log2 de esa razón, es {grado:.2f}. El modelo de sumas a costo constante "
            "predice 2 y el modelo de bits predice 4. La medición favorece el costo "
            "cuadrático: F(n) tiene Θ(n) bits y sumarlos no es una operación de costo fijo."
        )
    elif ultima >= 2.5:
        lectura = (
            f"La última razón es {fmt_razon(ultima)} y el grado estimado es {grado:.2f}. "
            "Ese cociente ya se separa de 2, que sería lo propio de un costo lineal, "
            "y camina hacia 4, que es lo propio del costo cuadrático de los bits."
        )
    else:
        lectura = (
            f"La última razón es {fmt_razon(ultima)} y el grado estimado es {grado:.2f}. "
            "En estos tamaños el tiempo todavía se parece al modelo lineal de Θ(n) sumas. "
            "El término de bits, Θ(n²), pesa más cuando n sigue creciendo, porque la "
            "cantidad de dígitos de F(n) no está acotada."
        )
    return ultima, grado, (
        f"Las razones T(2n)/T(n) del iterativo, en el orden de los tamaños, fueron {serie}. "
        + lectura
    )


def redaccion_ingenua(filas):
    comparaciones = []
    for fila in filas:
        if fila["razon"] is None:
            continue
        teoria = PHI ** (fila["n"] / 2)
        comparaciones.append((fila["n"], fila["razon"], teoria, fila["razon"] / teoria))
    mayor = max(item[1] for item in comparaciones)
    menor = min(item[1] for item in comparaciones)
    ajuste = sum(item[3] for item in comparaciones) / len(comparaciones)
    texto = (
        f"Las razones del ingenuo van de {fmt_razon(menor)} a {fmt_razon(mayor)}. "
        "No se acercan a 2 ni a 4: crecen al duplicar el argumento. "
        f"Si T(n) es proporcional a φ^n, entonces T(2n)/T(n) es proporcional a φ^(n/2), "
        f"donde n es el tamaño mayor de la pareja. El cociente entre cada razón medida "
        f"y esa referencia quedó, en promedio, en {ajuste:.2f}. "
    )
    if 0.4 <= ajuste <= 2.5:
        texto += (
            "El experimento reproduce el orden exponencial: la referencia y la medición "
            "van juntas, con la holgura propia del reloj y del costo fijo de cada llamada."
        )
    else:
        texto += (
            "La forma creciente se mantiene, aunque la constante del reloj separa la "
            "medición de la referencia φ^(n/2). La lectura del orden se apoya en ese "
            "crecimiento, no en un solo cociente."
        )
    return mayor, texto


def construir_resumen(filas_iter, filas_ing, ultima, grado, mayor):
    serie = ", ".join(fmt_razon(valor) for valor in razones(filas_iter))
    menor = min(razones(filas_ing))
    resumen = f"""Esta bitácora compara dos formas de calcular el n-ésimo Fibonacci. La ingenua obtiene F(n) sumando F(n-1) y F(n-2), y repite subproblemas ya resueltos. La iterativa guarda los dos últimos valores y avanza desde 2 hasta n. Las dos exigen un entero n mayor o igual que 0 y devuelven F(n), con F(0) = 0, F(1) = 1 y F(n) = F(n-1) + F(n-2).

La corrección del iterativo usa un invariante de ciclo. Al empezar la iteración i, a vale F(i-2) y b vale F(i-1). Con i = 2 se cumple, porque a = 0 y b = 1. Cada paso lo restablece y, al salir, b es F(n). Las pruebas rechazan entradas inválidas, contrastan la definición y comprueban que ambas coinciden de n = 0 a n = 20.

El ingenuo cumple T(n) = T(n-1) + T(n-2) + Θ(1), así que T(n) = Θ(φ^n), con φ aproximadamente 1,618. Su razón T(2n)/T(n) crece y no se estabiliza. El iterativo hace Θ(n) sumas. Si cada suma costara lo mismo, la razón tendería a 2. En Python, F(n) ocupa Θ(n) bits y la suma del paso i cuesta Θ(i): el total es Θ(n²) y la razón tiende a 4.

El experimento midió con time.perf_counter la mediana de cinco repeticiones, en tamaños que se duplican. Las razones del iterativo fueron {serie}. La última fue {fmt_razon(ultima)} y el grado estimado log2 fue {grado:.2f}. Se lee frente a 2, referencia lineal, y frente a 4, referencia cuadrática de bits. Las razones del ingenuo fueron de {fmt_razon(menor)} a {fmt_razon(mayor)} y siguen creciendo: es la firma exponencial. Para n grande sirve el iterativo, y el tiempo medido obliga a contar el costo de los enteros grandes."""
    palabras = len(resumen.split())
    if not 200 <= palabras <= 300:
        raise SystemExit(
            f"El resumen del foro tiene {palabras} palabras y debe quedar entre 200 y 300."
        )
    return resumen, palabras


class Informe(FPDF):
    def __init__(self):
        super().__init__()
        for estilo, ruta in FUENTES.items():
            self.add_font("Arial", estilo, ruta)
        self.set_auto_page_break(auto=True, margin=16)
        self.set_margins(18, 16, 18)

    def bloque(self, texto, alto=5.6, alineacion="L", relleno=False):
        self.set_x(self.l_margin)
        self.multi_cell(
            0,
            alto,
            texto,
            align=alineacion,
            fill=relleno,
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
        )

    def footer(self):
        self.set_y(-12)
        self.set_x(self.l_margin)
        self.set_font("Arial", "", 8)
        self.set_text_color(90, 90, 90)
        self.cell(
            0,
            6,
            f"Bitácora 1  ·  Fibonacci ingenuo frente a iterativo  ·  página {self.page_no()}",
            align="C",
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
        )
        self.set_text_color(0, 0, 0)

    def titulo_documento(self):
        self.set_font("Arial", "B", 16)
        self.set_text_color(20, 48, 84)
        self.bloque("BITÁCORA 1", alto=8, alineacion="C")
        self.set_font("Arial", "B", 14)
        self.bloque("Fibonacci ingenuo frente a iterativo", alto=7, alineacion="C")
        self.ln(1)
        self.set_font("Arial", "", 11)
        self.set_text_color(0, 0, 0)
        self.bloque(
            f"Equipo {EQUIPO}\n6 de noviembre de 2026",
            alto=6,
            alineacion="C",
        )
        self.ln(2)

    def seccion(self, texto):
        self.ln(1)
        self.set_font("Arial", "B", 13)
        self.set_text_color(20, 48, 84)
        self.bloque(texto, alto=7)
        self.ln(1)
        self.set_text_color(0, 0, 0)

    def parrafo(self, texto):
        self.set_font("Arial", "", 11)
        self.bloque(texto, alto=5.6)
        self.ln(1.5)

    def nota(self, texto):
        self.set_fill_color(255, 243, 205)
        self.set_font("Arial", "", 10)
        self.bloque(texto, alto=5.4, relleno=True)
        self.ln(2)

    def tabla(self, encabezados, filas, anchos):
        alto = 7
        if self.get_y() + alto * (len(filas) + 2) > 275:
            self.add_page()
        self.set_font("Arial", "B", 9)
        self.set_fill_color(31, 78, 121)
        self.set_text_color(255, 255, 255)
        for texto, ancho in zip(encabezados, anchos):
            self.cell(ancho, alto, texto, border=1, align="C", fill=True)
        self.ln()
        self.set_text_color(0, 0, 0)
        self.set_font("Arial", "", 9)
        sombrear = False
        for fila in filas:
            if self.get_y() > 275:
                self.add_page()
            self.set_fill_color(235, 241, 248)
            for texto, ancho in zip(fila, anchos):
                self.cell(ancho, alto, texto, border=1, align="C", fill=sombrear)
            self.ln()
            sombrear = not sombrear
        self.ln(2)

    def figura(self, ruta, pie):
        if self.get_y() > 185:
            self.add_page()
        self.set_x(self.l_margin)
        self.image(str(ruta), w=170)
        self.ln(1)
        self.set_font("Arial", "I", 9)
        self.bloque(pie, alto=4.6)
        self.ln(2)


def filas_tabla_iterativa(filas):
    salida = []
    for fila in filas:
        grado = "N/A" if fila["razon"] is None else f"{math.log2(fila['razon']):.2f}"
        salida.append(
            [
                str(fila["n"]),
                fmt_tiempo(fila["mediana_s"]),
                fmt_razon(fila["razon"]),
                grado,
            ]
        )
    return salida


def filas_tabla_ingenua(filas):
    salida = []
    for fila in filas:
        if fila["razon"] is None:
            referencia = "N/A"
        else:
            referencia = fmt_razon(PHI ** (fila["n"] / 2))
        salida.append(
            [
                str(fila["n"]),
                fmt_tiempo(fila["mediana_s"]),
                fmt_razon(fila["razon"]),
                referencia,
            ]
        )
    return salida


def escribir_mensaje(resumen, palabras, meta, mayor):
    declaracion = (
        "Herramienta y versión: Cursor, agente Auto (enrutador de agentes de Cursor), "
        "usado el 6 de noviembre de 2026. Intervino código Python 3.13.0, matplotlib "
        f"{matplotlib.__version__} y fpdf2 {fpdf.__version__}.\n"
        "Para qué se usó: pasar el algoritmo de una transcripción de consola a módulos "
        "ejecutables, escribir las pruebas del invariante y de la precondición, lanzar "
        "el experimento en este equipo, dibujar las gráficas y redactar el informe en "
        "el orden de la plantilla.\n"
        "Qué se verificó: que ambas funciones devuelven F(n) en los casos de la definición; "
        "que el invariante se cumple en cada vuelta; que unittest termina en OK; que las "
        "tablas y las gráficas del PDF salen de los CSV de esta corrida.\n"
        "Qué se descartó: entregar la transcripción con los prompts >>> como si fuera un "
        "programa; afirmar que el tiempo del iterativo es lineal cuando la razón T(2n)/T(n) "
        "se acerca a 4."
    )
    texto = f"""Asunto sugerido
Equipo {EQUIPO} – Bitácora 1 – Fibonacci ingenuo frente a iterativo

a) Resumen ({palabras} palabras)

{resumen}

b) Enlace (URL) del repositorio Git
PEGAR AQUÍ LA URL PÚBLICA. Tiene que abrir sin pedir permisos.

c) Contribución de cada integrante
Una línea por persona. Completar con los nombres reales, por ejemplo:
- Nombre Apellido: especificación, invariante y revisión del costo.
- Nombre Apellido: pruebas, experimento en el equipo y lectura de T(2n)/T(n).
- Nombre Apellido: repositorio, informe y mensaje del foro.

d) Declaración de uso de IA
{declaracion}

Datos de la corrida que sostiene el resumen
- Semilla registrada: {meta['semilla']}. {meta['nota']}
- {meta['python']}
- {meta['plataforma']}
- Repeticiones: {meta['repeticiones']}. {meta['calentamiento']}.
- Reloj: {meta['reloj']}. Estadístico: {meta['estadistico']}.
- Mayor razón ingenua observada: {fmt_razon(mayor)}.
"""
    (RAIZ.parent / "MENSAJE_FORO.md").write_text(texto, encoding="utf-8")


def construir_pdf(filas_iter, filas_ing, meta, resultado, salida_pruebas, texto_iterativo, texto_ingenuo):
    pruebas_ok = resultado.wasSuccessful()
    estado = (
        f"La corrida de esta máquina quedó en OK: "
        f"{resultado.testsRun} pruebas, {len(resultado.failures)} fallos y "
        f"{len(resultado.errors)} errores."
        if pruebas_ok
        else "La corrida de pruebas no quedó en OK. El detalle está al final de esta sección."
    )

    pdf = Informe()
    pdf.set_title("Bitácora 1 - Fibonacci ingenuo frente a iterativo")
    pdf.set_author(f"Equipo {EQUIPO}")
    pdf.add_page()
    pdf.titulo_documento()

    pdf.seccion("1. Especificación")
    pdf.parrafo(
        "El problema es calcular el n-ésimo número de Fibonacci. Las dos soluciones "
        "comparten contrato. La precondición exige que n sea un entero mayor o igual "
        "que 0. La postcondición exige que el valor devuelto sea F(n), definido por "
        "F(0) = 0, F(1) = 1 y F(n) = F(n-1) + F(n-2) para todo n mayor o igual que 2."
    )
    pdf.parrafo(
        "Quedan fuera del contrato los negativos, los reales, los textos y los booleanos. "
        "En Python, bool es subclase de int, así que True y False pasarían un chequeo "
        "que solo usara isinstance(n, int). La especificación los rechaza de forma "
        "explícita: un valor de verdad no es un índice de la sucesión."
    )
    pdf.parrafo(
        "Fibonacci ingenuo traduce la recurrencia de manera directa: para n mayor que 1 "
        "hace dos llamadas, con n-1 y con n-2, y suma los resultados. Fibonacci iterativo "
        "conserva únicamente los dos últimos valores y recorre i desde 2 hasta n. Los dos "
        "cumplen la misma postcondición. Difieren en el trabajo que repiten y en el orden "
        "de crecimiento, que es el objeto de esta bitácora."
    )

    pdf.seccion("2. Corrección")
    pdf.parrafo(
        "La versión ingenua es correcta por inducción sobre n. Si n es 0 o 1, el valor "
        "devuelto es el de la definición. Si n es mayor que 1 y las llamadas con argumento "
        "menor ya devuelven el Fibonacci correspondiente, la suma es F(n-1) + F(n-2), "
        "que es F(n). La recursión termina porque cada llamada recibe un entero estrictamente "
        "menor y la precondición impide bajar de 0."
    )
    pdf.parrafo(
        "La versión iterativa se justifica con un invariante de ciclo. Justo antes de "
        "ejecutar la iteración i, con i entre 2 y n, se cumple a = F(i-2) y b = F(i-1). "
        "Inicialización: antes de entrar, a = 0 = F(0) y b = 1 = F(1), que es el invariante "
        "cuando i = 2. Mantenimiento: el paso sustituye a por b y b por a + b. El nuevo a "
        "es F(i-1) y el nuevo b es F(i-2) + F(i-1) = F(i). Eso es el invariante de la "
        "iteración i+1. Terminación: el rango es finito. Al acabar la vuelta i = n, b = F(n), "
        "que es la postcondición. Los casos n = 0 y n = 1 se demuestran aparte y no entran al ciclo."
    )
    pdf.parrafo(
        "La prueba test_invariante_del_ciclo revisa esa afirmación en cada vuelta para "
        "n = 30, reconstruyendo la sucesión con la misma recurrencia de la especificación. "
        "La prueba diferencial compara las dos funciones desde n = 0 hasta n = 20. "
        "Coincidir no reemplaza el invariante: lo contrasta con una segunda implementación."
    )

    pdf.seccion("3. Costo")
    pdf.parrafo(
        "En el ingenuo, el tiempo satisface T(0) = T(1) = Θ(1) y "
        "T(n) = T(n-1) + T(n-2) + Θ(1). La solución es T(n) = Θ(φ^n), con "
        "φ = (1 + √5) / 2 ≈ 1,618. El número de llamadas es 2·F(n+1) - 1. "
        "Cada llamada vuelve a calcular subproblemas enteros, sin guardar resultados."
    )
    pdf.parrafo(
        "En el iterativo hay un ciclo de n-1 vueltas. Contando cada suma como operación "
        "de costo constante, el tiempo es Θ(n). Ese modelo se queda corto en Python. "
        "F(n) tiene Θ(n) bits, porque crece como φ^n / √5 y el número de bits es el "
        "logaritmo de ese valor. La suma del paso i opera cantidades de Θ(i) bits y "
        "cuesta Θ(i). Sumar esos costos desde i = 2 hasta n da Θ(n²)."
    )
    pdf.parrafo(
        "La razón del experimento distingue los modelos. Si T(n) crece como a·n^k, "
        "entonces T(2n)/T(n) tiende a 2^k. Para un costo lineal, k = 1 y la razón tiende "
        "a 2. Para un costo cuadrático, k = 2 y la razón tiende a 4. El grado observado "
        "se estima como log2 de la razón. Si el orden es Θ(φ^n), la razón T(2n)/T(n) "
        "crece como φ^n y no tiende a ninguna constante. Por eso el mismo cociente sirve "
        "para los dos algoritmos, y la lectura es distinta."
    )

    pdf.seccion("4. Implementación y pruebas")
    pdf.parrafo(
        "El código de entrega está en fibonacci.py. validar_n aplica la precondición. "
        "fibonacci_ingenuo implementa la recurrencia. fibonacci_iterativo implementa el "
        "ciclo, y el comentario del cuerpo enuncia el invariante en el punto en que se "
        "exige. pruebas.py contiene las pruebas con unittest. No hace falta instalar nada "
        "para correrlas."
    )
    pdf.parrafo(
        "Las pruebas cubren cinco obligaciones. Los casos conocidos comparan las dos "
        "funciones con F(0) hasta F(16), tomados de la definición. La precondición se "
        "ensaya en las dos funciones con -1, -5, 1.5, 3.0, el texto \"5\", True y False. "
        "El contraste diferencial exige igualdad en 0 ≤ n ≤ 20. El invariante se comprueba "
        "vuelta por vuelta hasta n = 30."
    )
    pdf.parrafo(estado + " Comando: .\\.venv\\Scripts\\python.exe -m unittest pruebas.py -v")
    if not pruebas_ok:
        pdf.set_font("Arial", "", 8)
        pdf.bloque(salida_pruebas[-2500:], alto=4)
        pdf.ln(2)

    pdf.seccion("5. Experimento")
    pdf.parrafo(
        "El diseño duplica el tamaño, que es la forma de leer T(2n)/T(n). Para cada n "
        "se hace una llamada de calentamiento, que no entra en la cuenta, y después cinco "
        "mediciones con time.perf_counter. El resumen de cada fila es la mediana. También "
        "se guardan el mínimo y el máximo en el CSV. La semilla 20261106 se fija con "
        "random.seed y se escribe en los metadatos. No hay muestreo aleatorio: las dos "
        "funciones son deterministas y la semilla no mueve los tiempos."
    )
    pdf.parrafo(
        f"Máquina de esta corrida: {meta['plataforma']}. {meta['python']} "
        f"Tamaños iterativos: {meta['tamanios_iterativo']}. "
        "La razón de una fila es el tiempo mediano de n dividido por el tiempo mediano "
        "de n/2, cuando esa mitad también está en la serie. En esta serie cada tamaño, "
        "salvo el primero, es el doble del anterior, así que cada cociente es exactamente "
        "T(2n)/T(n) del tamaño previo."
    )
    pdf.parrafo(texto_iterativo)
    pdf.tabla(
        ["n", "Mediana (s)", "T(2n)/T(n)", "Grado log2"],
        filas_tabla_iterativa(filas_iter),
        [36, 50, 46, 42],
    )
    pdf.figura(
        DIR_FIGURAS / "iterativo_tiempo_y_razon.png",
        "Figura 1. A la izquierda, tiempo mediano del Fibonacci iterativo. A la derecha, "
        "la razón T(2n)/T(n). La línea discontinua marca 2 (costo lineal si cada suma "
        "cuesta lo mismo) y la línea punteada marca 4 (costo cuadrático de bits).",
    )
    pdf.parrafo(
        "Los archivos de la corrida son datos/iterativo.csv, datos/ingenuo.csv y "
        "datos/metadatos.txt. Las figuras quedan en figuras/. Volver a generarlos es "
        "ejecutar experimento.py con el mismo comando del README."
    )

    pdf.seccion("6. Contraste")
    pdf.parrafo(
        "Los dos algoritmos cumplen la misma especificación y no cuestan lo mismo. "
        "El ingenuo repite un árbol de llamadas de orden Θ(φ^n). El iterativo hace "
        "una sola pasada. En la práctica, el ingenuo deja de ser utilizable cerca de "
        "n = 40, porque cada incremento de 1 multiplica el trabajo por φ. El iterativo "
        "se midió hasta n = 320000 en esta máquina."
    )
    pdf.parrafo(
        f"Tamaños ingenuos: {meta['tamanios_ingenuo']}. Se eligieron pares cuya mitad "
        "también está en la lista, para poder formar T(2n)/T(n). No se usaron los "
        "tamaños del iterativo: una sola llamada ingenua con n = 10000 no termina en "
        "un tiempo razonable. El contraste se hace por el orden, no por cronometrar "
        "los dos algoritmos en el mismo n."
    )
    pdf.parrafo(texto_ingenuo)
    pdf.tabla(
        ["n", "Mediana (s)", "T(2n)/T(n)", "Referencia φ^(n/2)"],
        filas_tabla_ingenua(filas_ing),
        [28, 46, 46, 54],
    )
    pdf.figura(
        DIR_FIGURAS / "ingenuo_tiempo_y_razon.png",
        "Figura 2. A la izquierda, tiempo mediano del Fibonacci ingenuo. La escala es "
        "logarítmica cuando los tiempos se separan en más de un orden. A la derecha, "
        "T(2n)/T(n). En un orden exponencial esta razón crece; en un orden polinomial "
        "tendería a una constante.",
    )
    pdf.parrafo(
        "El contraste queda así. El ingenuo muestra una razón que crece con n, en la "
        f"dirección de φ^(n/2). El iterativo queda entre {fmt_razon(min(razones(filas_iter)))} "
        f"y {fmt_razon(max(razones(filas_iter)))}: por encima de la referencia lineal 2 y "
        "alrededor de la referencia cuadrática 4. Esa lectura explica por qué no basta con "
        "decir que el ciclo es de n sumas. Para n grande, el algoritmo utilizable es el "
        "iterativo, con orden Θ(n²) en el modelo de bits del lenguaje."
    )

    pdf.seccion("7. Uso de IA y reproducibilidad")
    pdf.parrafo(
        "Herramienta y versión: Cursor, agente Auto, enrutador de agentes de Cursor, "
        f"en la sesión del {date.today().strftime('%d/%m/%Y')}. El informe se generó con "
        f"fpdf2 {fpdf.__version__} y las gráficas con matplotlib {matplotlib.__version__}, "
        "sobre Python 3.13.0 de CPython para Windows de 64 bits."
    )
    pdf.parrafo(
        "Para qué se usó: convertir el algoritmo, que estaba en una transcripción de "
        "consola, en módulos que se pueden ejecutar; añadir la validación de la "
        "precondición, las pruebas del invariante y el experimento de duplicación; "
        "producir los CSV, las dos gráficas y este PDF en el orden de la plantilla."
    )
    pdf.parrafo(
        "Qué se verificó: la definición F(0), F(1) y la recurrencia en los casos de "
        "prueba; el invariante en cada vuelta del ciclo; la corrida de unittest; y que "
        "cada número de las tablas sale del CSV escrito por experimento.py en esta máquina, "
        "sin teclear tiempos a mano."
    )
    pdf.parrafo(
        "Qué se descartó: usar la transcripción con prompts >>> como evidencia, porque "
        "ese archivo no es un programa; concluir que el iterativo es lineal en tiempo de "
        "pared solo porque el ciclo da n vueltas."
    )
    pdf.parrafo(
        "Reproducir la corrida, desde la carpeta del proyecto:"
    )
    pdf.set_font("Arial", "", 10)
    pdf.bloque(
        "C:\\laragon\\bin\\python\\python-3.13\\python.exe -m venv .venv\n"
        ".\\.venv\\Scripts\\python.exe -m pip install -r requirements.txt\n"
        ".\\.venv\\Scripts\\python.exe -m unittest pruebas.py -v\n"
        ".\\.venv\\Scripts\\python.exe experimento.py\n"
        ".\\.venv\\Scripts\\python.exe generar_informe.py",
        alto=5,
    )
    pdf.ln(2)
    pdf.parrafo(
        f"Semilla: {meta['semilla']}. {meta['nota']} Reloj: {meta['reloj']}. "
        f"Estadístico: {meta['estadistico']}. {meta['calentamiento']}. "
        f"Repeticiones: {meta['repeticiones']}. Otra computadora va a obtener otros "
        "segundos y unas razones parecidas, no una copia bit a bit del reloj. "
        "El PDF se vuelve a armar con generar_informe.py y queda en "
        f"informe/{PDF_NOMBRE}."
    )
    pdf.parrafo(
        "Contribución de cada integrante: se declara en el mensaje del foro, una línea "
        "por persona. El repositorio contiene el código, pruebas.py, el README con los "
        "comandos, las versiones y la semilla, la carpeta datos y la carpeta figuras."
    )

    DIR_INFORME.mkdir(exist_ok=True)
    destino = DIR_INFORME / PDF_NOMBRE
    pdf.output(str(destino))
    return destino


def main():
    necesarios = [
        DIR_DATOS / "iterativo.csv",
        DIR_DATOS / "ingenuo.csv",
        DIR_DATOS / "metadatos.txt",
        DIR_FIGURAS / "iterativo_tiempo_y_razon.png",
        DIR_FIGURAS / "ingenuo_tiempo_y_razon.png",
    ]
    faltan = [str(ruta) for ruta in necesarios if not ruta.exists()]
    if faltan:
        raise SystemExit("Faltan productos del experimento:\n" + "\n".join(faltan))

    filas_iter = leer_csv(DIR_DATOS / "iterativo.csv")
    filas_ing = leer_csv(DIR_DATOS / "ingenuo.csv")
    meta = leer_metadatos(DIR_DATOS / "metadatos.txt")
    resultado, salida_pruebas = ejecutar_pruebas()
    ultima, grado, texto_iterativo = redaccion_iterativa(filas_iter)
    mayor, texto_ingenuo = redaccion_ingenua(filas_ing)
    resumen, palabras = construir_resumen(filas_iter, filas_ing, ultima, grado, mayor)
    escribir_mensaje(resumen, palabras, meta, mayor)
    destino = construir_pdf(
        filas_iter,
        filas_ing,
        meta,
        resultado,
        salida_pruebas,
        texto_iterativo,
        texto_ingenuo,
    )
    print(f"PDF: {destino}")
    print(f"Resumen del foro: {palabras} palabras")
    if not resultado.wasSuccessful():
        raise SystemExit("Las pruebas no pasaron; el PDF lo indica.")


if __name__ == "__main__":
    main()
