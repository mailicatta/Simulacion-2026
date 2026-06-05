"""
TP 2.1 - GENERADORES PSEUDOALEATORIOS
Universidad Tecnológica Nacional - FRRO
Simulación 2026

Autor: Licatta, Maite
"""

import math
import time
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats


# =============================================================================
# SECCIÓN 1: GENERADORES PSEUDOALEATORIOS
# =============================================================================

class GeneradorCuadradosMedios:
    """
    Método de los Cuadrados Medios
    John von Neumann (1946)
    """

    def __init__(self, semilla: int, digitos: int = 4):

        self.semilla = semilla
        self.digitos = digitos
        self._estado = semilla

    def siguiente(self) -> float:

        cuadrado = self._estado ** 2

        cuadrado_str = str(cuadrado).zfill(2 * self.digitos)

        inicio = (len(cuadrado_str) - self.digitos) // 2

        medio = cuadrado_str[inicio: inicio + self.digitos]

        self._estado = int(medio)

        return self._estado / (10 ** self.digitos)

    def generar(self, n: int) -> list:

        return [self.siguiente() for _ in range(n)]


# =============================================================================

class GeneradorGCL:
    """
    Generador Congruencial Lineal
    """

    PARAMS = {
        "Numerical Recipes": {
            "a": 1664525,
            "c": 1013904223,
            "m": 2**32
        },

        "RANDU (deficiente)": {
            "a": 65539,
            "c": 0,
            "m": 2**31
        },

        "POSIX Standard": {
            "a": 1103515245,
            "c": 12345,
            "m": 2**31
        }
    }

    def __init__(
        self,
        semilla: int,
        preset: str = "Numerical Recipes"
    ):

        params = self.PARAMS[preset]

        self.a = params["a"]
        self.c = params["c"]
        self.m = params["m"]

        self.nombre_preset = preset

        self._estado = semilla

    def siguiente(self) -> float:

        self._estado = (
            self.a * self._estado + self.c
        ) % self.m

        return self._estado / self.m

    def generar(self, n: int) -> list:

        return [self.siguiente() for _ in range(n)]


# =============================================================================

class GeneradorXorShift64:
    """
    Generador XorShift 64 bits
    """

    def __init__(self, semilla: int):

        if semilla == 0:
            semilla = 88172645463325252

        self._estado = np.uint64(semilla)

    def siguiente(self) -> float:

        x = self._estado

        x ^= x << np.uint64(13)
        x ^= x >> np.uint64(7)
        x ^= x << np.uint64(17)

        self._estado = x

        return float(x) / float(np.iinfo(np.uint64).max)

    def generar(self, n: int) -> list:

        return [self.siguiente() for _ in range(n)]


# =============================================================================

class GeneradorPython:
    """
    Generador Mersenne Twister de Python
    """

    def __init__(self, semilla: int = None):

        self.semilla = (
            semilla
            if semilla is not None
            else int(time.time())
        )

        self.rng = np.random.default_rng(self.semilla)

    def generar(self, n: int) -> list:

        return list(self.rng.random(n))


# =============================================================================
# SECCIÓN 2: TESTS ESTADÍSTICOS
# =============================================================================

class TestsEstadisticos:

    NIVEL_SIGNIFICANCIA = 0.05

    # =========================================================================

    @staticmethod
    def test_chi_cuadrado(
        muestra: list,
        k: int = 10
    ) -> dict:

        n = len(muestra)

        esperado = n / k

        conteos = [0] * k

        for x in muestra:

            idx = min(int(x * k), k - 1)

            conteos[idx] += 1

        chi2 = sum(
            (obs - esperado) ** 2 / esperado
            for obs in conteos
        )

        gl = k - 1

        p_valor = 1 - stats.chi2.cdf(chi2, df=gl)

        return {
            "nombre": "Chi-Cuadrado",
            "p_valor": p_valor,
            "aprueba": (
                p_valor >
                TestsEstadisticos.NIVEL_SIGNIFICANCIA
            )
        }

    # =========================================================================

    @staticmethod
    def test_ks(muestra: list) -> dict:

        _, p_valor = stats.kstest(
            muestra,
            'uniform'
        )

        return {
            "nombre": "Kolmogorov-Smirnov",
            "p_valor": p_valor,
            "aprueba": (
                p_valor >
                TestsEstadisticos.NIVEL_SIGNIFICANCIA
            )
        }

    # =========================================================================

    @staticmethod
    def test_rachas(muestra: list) -> dict:

        n = len(muestra)

        mediana = np.median(muestra)

        signos = [
            1 if x >= mediana else 0
            for x in muestra
        ]

        n1 = sum(signos)

        n2 = n - n1

        rachas = 1

        for i in range(1, len(signos)):

            if signos[i] != signos[i - 1]:

                rachas += 1

        mu_r = (2 * n1 * n2) / n + 1

        sigma2_r = (
            (
                2 * n1 * n2 *
                (2 * n1 * n2 - n)
            ) /
            (
                n ** 2 * (n - 1)
            )
            if n > 1 else 0
        )

        if sigma2_r <= 0 or n1 == 0 or n2 == 0:

            return {
                "nombre": "Rachas",
                "p_valor": 0.0,
                "aprueba": False
            }

        z = (
            (rachas - mu_r) /
            math.sqrt(sigma2_r)
        )

        p_valor = 2 * (
            1 - stats.norm.cdf(abs(z))
        )

        return {
            "nombre": "Rachas",
            "p_valor": p_valor,
            "aprueba": (
                p_valor >
                TestsEstadisticos.NIVEL_SIGNIFICANCIA
            )
        }

    # =========================================================================

    @staticmethod
    def test_autocorrelacion(
        muestra: list,
        lags: list = None
    ) -> dict:

        if lags is None:

            lags = [1, 2, 5, 10]

        n = len(muestra)

        mu = np.mean(muestra)

        sigma2 = np.var(muestra)

        if sigma2 == 0:

            return {
                "nombre": "Autocorrelación",
                "aprueba": False
            }

        significativos = False

        for k in lags:

            r_k = sum(
                (
                    muestra[i] - mu
                ) * (
                    muestra[i + k] - mu
                )
                for i in range(n - k)
            ) / ((n - k) * sigma2)

            se = 1 / math.sqrt(n)

            z = r_k / se

            p_valor = 2 * (
                1 - stats.norm.cdf(abs(z))
            )

            if (
                p_valor <
                TestsEstadisticos.NIVEL_SIGNIFICANCIA
            ):

                significativos = True

        return {
            "nombre": "Autocorrelación",
            "aprueba": not significativos
        }


# =============================================================================
# SECCIÓN 3: GRÁFICOS
# =============================================================================

def crear_grilla(cantidad):

    columnas = min(3, cantidad)

    filas = math.ceil(cantidad / columnas)

    fig, axes = plt.subplots(
        filas,
        columnas,
        figsize=(5 * columnas, 4 * filas)
    )

    if filas == 1 and columnas == 1:

        axes = [axes]

    elif filas == 1 or columnas == 1:

        axes = axes.flatten()

    else:

        axes = axes.flatten()

    return fig, axes


# =============================================================================

def graficar_histograma(
    muestras: dict,
    n: int,
    filename: str
):

    fig, axes = crear_grilla(len(muestras))

    for ax, (nombre, muestra) in zip(
        axes,
        muestras.items()
    ):

        ax.hist(
            muestra,
            bins=20,
            edgecolor='black',
            color='steelblue',
            alpha=0.8
        )

        ax.axhline(
            y=n / 20,
            color='red',
            linestyle='--'
        )

        ax.set_title(
            nombre,
            fontsize=10,
            fontweight='bold'
        )

        ax.grid(axis='y', alpha=0.3)

    for ax in axes[len(muestras):]:

        ax.axis('off')

    plt.tight_layout()

    plt.savefig(filename, dpi=150)

    plt.close()


# =============================================================================

def graficar_dispersion_fases(
    muestras: dict,
    filename: str
):

    fig, axes = crear_grilla(len(muestras))

    for ax, (nombre, muestra) in zip(
        axes,
        muestras.items()
    ):

        ax.scatter(
            muestra[:-1],
            muestra[1:],
            s=2,
            alpha=0.5,
            color='darkcyan'
        )

        ax.set_title(
            nombre,
            fontsize=10,
            fontweight='bold'
        )

        ax.set_xlim(0, 1)

        ax.set_ylim(0, 1)

        ax.grid(alpha=0.3)

    for ax in axes[len(muestras):]:

        ax.axis('off')

    plt.tight_layout()

    plt.savefig(filename, dpi=150)

    plt.close()


# =============================================================================

def graficar_serie_temporal(
    muestras: dict,
    filename: str
):

    fig, axes = crear_grilla(len(muestras))

    for ax, (nombre, muestra) in zip(
        axes,
        muestras.items()
    ):

        ax.plot(
            muestra[:200],
            linewidth=0.8,
            color='crimson'
        )

        ax.axhline(
            0.5,
            color='black',
            linestyle='--',
            alpha=0.5
        )

        ax.set_title(
            nombre,
            fontsize=10,
            fontweight='bold'
        )

        ax.set_ylim(-0.05, 1.05)

        ax.grid(alpha=0.3)

    for ax in axes[len(muestras):]:

        ax.axis('off')

    plt.tight_layout()

    plt.savefig(filename, dpi=150)

    plt.close()


# =============================================================================

def graficar_autocorrelacion(
    muestras: dict,
    filename: str
):

    fig, axes = crear_grilla(len(muestras))

    for ax, (nombre, muestra) in zip(
        axes,
        muestras.items()
    ):

        n = len(muestra)

        mu = np.mean(muestra)

        sigma2 = np.var(muestra)

        lags = range(1, 31)

        r_ks = []

        for k in lags:

            if sigma2 == 0:

                r_ks.append(1.0)

            else:

                r_k = sum(
                    (
                        muestra[i] - mu
                    ) * (
                        muestra[i + k] - mu
                    )
                    for i in range(n - k)
                ) / ((n - k) * sigma2)

                r_ks.append(r_k)

        ax.bar(
            lags,
            r_ks,
            color='purple',
            alpha=0.7
        )

        ic = 1.96 / math.sqrt(n)

        ax.axhline(
            ic,
            color='red',
            linestyle='--'
        )

        ax.axhline(
            -ic,
            color='red',
            linestyle='--'
        )

        ax.set_title(
            nombre,
            fontsize=10,
            fontweight='bold'
        )

        ax.set_ylim(-1.05, 1.05)

        ax.grid(alpha=0.3)

    for ax in axes[len(muestras):]:

        ax.axis('off')

    plt.tight_layout()

    plt.savefig(filename, dpi=150)

    plt.close()


# =============================================================================
# SECCIÓN 4: MAIN
# =============================================================================

def main():

    SEMILLA = 1265

    N = 1000

    print("=" * 80)

    print(
        f" EJECUTANDO DIAGNÓSTICO ESTADÍSTICO "
        f"(N = {N} | SEMILLA = {SEMILLA})"
    )

    print("=" * 80)

    # =========================================================================
    # GENERADORES
    # =========================================================================

    generadores = {

        "Cuadrados Medios":
            GeneradorCuadradosMedios(
                semilla=6752
            ),

        "GCL Numerical":
            GeneradorGCL(
                SEMILLA,
                preset="Numerical Recipes"
            ),

        "GCL RANDU":
            GeneradorGCL(
                SEMILLA,
                preset="RANDU (deficiente)"
            ),

        "GCL POSIX":
            GeneradorGCL(
                SEMILLA,
                preset="POSIX Standard"
            ),

        "XorShift 64":
            GeneradorXorShift64(
                SEMILLA
            ),

        "Python Random":
            GeneradorPython(
                SEMILLA
            )
    }

    # =========================================================================
    # MUESTRAS
    # =========================================================================

    muestras = {
        nombre: gen.generar(N)
        for nombre, gen in generadores.items()
    }

    # =========================================================================
    # TESTS
    # =========================================================================

    resultados = {}

    for nombre, muestra in muestras.items():

        resultados[nombre] = {

            "Chi-Cuadrado":
                TestsEstadisticos.test_chi_cuadrado(
                    muestra
                ),

            "Kolmogorov-Smirnov":
                TestsEstadisticos.test_ks(
                    muestra
                ),

            "Rachas":
                TestsEstadisticos.test_rachas(
                    muestra
                ),

            "Autocorrelación":
                TestsEstadisticos.test_autocorrelacion(
                    muestra
                )
        }

    # =========================================================================
    # TABLA
    # =========================================================================

    header = (
        f"{'Generador':<25} | "
        f"{'Chi²':^12} | "
        f"{'KS':^12} | "
        f"{'Rachas':^12} | "
        f"{'Autocorr':^10}"
    )

    print(header)

    print("-" * len(header))

    for nombre, res in resultados.items():

        fila = f"{nombre:<25} | "

        for test in [
            "Chi-Cuadrado",
            "Kolmogorov-Smirnov",
            "Rachas"
        ]:

            estado = (
                "OK"
                if res[test]["aprueba"]
                else "FALLA"
            )

            fila += (
                f"{estado} "
                f"p={res[test]['p_valor']:.3f} | "
            )

        autocorr = (
            "OK"
            if res["Autocorrelación"]["aprueba"]
            else "FALLA"
        )

        fila += f"{autocorr:^10}"

        print(fila)

    print("-" * len(header))

    # =========================================================================
    # GRÁFICOS
    # =========================================================================

    print("\n[INFO] Generando gráficos...")

    graficar_histograma(
        muestras,
        N,
        "histogramas.png"
    )

    graficar_dispersion_fases(
        muestras,
        "dispersion.png"
    )

    graficar_serie_temporal(
        muestras,
        "serie_temporal.png"
    )

    graficar_autocorrelacion(
        muestras,
        "autocorrelacion.png"
    )

    print(
        "[ÉXITO] Archivos generados correctamente."
    )


# =============================================================================
# EJECUCIÓN
# =============================================================================

if __name__ == "__main__":

    main()
