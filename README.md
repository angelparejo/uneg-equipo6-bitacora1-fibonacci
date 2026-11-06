# Bitácora 1 — Fibonacci ingenuo frente a iterativo

**Universidad Nacional Experimental de Guayana (UNEG)**
Análisis y Diseño de Algoritmos · Prof. Ana Sosa
**Equipo 6**

| Integrante | Contribución |
|---|---|
| Angel Parejo | Repositorio Git, reproducción del experimento en Linux/WSL2 con Python 3.13.0, revisión crítica del análisis |
| _(pendiente)_ | _(pendiente)_ |

Comparación del Fibonacci recursivo ingenuo con el Fibonacci iterativo: especificación, invariante, costo, pruebas y experimento de la razón T(2n)/T(n).

## Versiones

- Python 3.13.0 (CPython, 64 bits).
- matplotlib 3.11.2 y fpdf2 2.9.0, fijadas en `requirements.txt`. Las pruebas usan solo la biblioteca estándar.
- La versión exacta de Python y la plataforma de cada corrida quedan en `metadatos.txt`.

## Semilla

`SEMILLA = 20261106`, fijada al inicio de `experimento.py` con `random.seed`.

El experimento no usa números aleatorios: cronometra dos funciones deterministas con `time.perf_counter` y resume cada tamaño con la mediana. La semilla se registra, pero no cambia los tiempos. En otra máquina los segundos cambian; las razones T(2n)/T(n) deben ser parecidas.

## Comandos

### Windows (PowerShell)

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m unittest pruebas.py -v
.\.venv\Scripts\python.exe experimento.py
.\.venv\Scripts\python.exe generar_informe.py
```

Si `py` no está instalado, usar la ruta del intérprete 3.13.0 (en la corrida original: `C:\laragon\bin\python\python-3.13\python.exe`).

### Linux / WSL

```bash
uv python install 3.13.0
$(uv python find 3.13.0) -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m unittest pruebas.py -v
.venv/bin/python experimento.py
```

El informe queda en `informe/Equipo_6_Bitacora1.pdf`.

## Resultados

| Carpeta | Corrida |
|---|---|
| `datos/`, `figuras/` | Windows 11, Python 3.13.0 (corrida del informe) |
| `datos/linux/`, `figuras/linux/` | Linux WSL2, Intel i5-8265U, Python 3.13.0 (reproducción) |

`experimento.py` siempre escribe en `datos/` y `figuras/`; la corrida de Linux se movió después a las subcarpetas `linux/`.

Cada carpeta tiene:

- `iterativo.csv` e `ingenuo.csv`: n, mediana, mínimo, máximo y razón T(2n)/T(n).
- `metadatos.txt`: semilla, versión de Python, plataforma, repeticiones y reloj.
- Las gráficas `iterativo_tiempo_y_razon.png` e `ingenuo_tiempo_y_razon.png`.

Protocolo: 1 llamada de calentamiento por cada n, fuera de la cuenta, y mediana de 5 repeticiones. Tamaños iterativos: 10000, 20000, 40000, 80000, 160000 y 320000. Tamaños ingenuos: 8, 10, 12, 14, 16, 20, 24, 28 y 32. La razón de una fila es el tiempo de n dividido por el tiempo de n/2.
