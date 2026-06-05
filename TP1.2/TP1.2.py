"""
TP 1.2 - Estudio Económico-Matemático de Apuestas en la Ruleta
Cátedra de Simulación - UTN FRRO
 
Uso:
    python TP1.2.py -c XXX -n YYY -s [m|d|f|o] -a [i|f]
    python TP1.2.py -c XXX -n YYY -e ZZ -s [m|d|f|o] -a [i|f]
 
Parámetros:
    -c  : capital inicial (ej: 1500)
    -n  : número de tiradas (ej: 25, 50, 100) — ignorado si -a f (agotar saldo)
    -e  : número específico sobre el que aplicar la estrategia (opcional)
    -s  : estrategia: m=Martingala, d=D'Alembert, f=Fibonacci, o=Paroli
    -a  : tipo de capital: i=infinito, f=finito (acotado)
 
Estrategias implementadas:
    m  - Martingala : dobla la apuesta tras cada pérdida, vuelve a la inicial al ganar
    d  - D'Alembert : sube 1 unidad tras perder, baja 1 unidad tras ganar
    f  - Fibonacci  : sube según Fibonacci al perder, retrocede 2 pasos al ganar
    o  - Paroli     : dobla la apuesta tras ganar (máx 3 victorias seguidas), vuelve al inicial al perder
"""
 
import random
import numpy as np
import matplotlib.pyplot as plt
import argparse
import sys
 
# ─────────────────────────────────────────────
# Constantes de la ruleta europea
# ─────────────────────────────────────────────
NUMEROS_ROJOS = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
APUESTA_INICIAL = 10
NUM_CORRIDAS = 5
COLORES_CORRIDAS = ["blue", "orange", "green", "red", "purple"]
 
# ─────────────────────────────────────────────
# Funciones auxiliares
# ─────────────────────────────────────────────
 
def girar_ruleta():
    """Devuelve un número entre 0 y 36."""
    return random.randint(0, 36)
 
def es_rojo(n):
    return n in NUMEROS_ROJOS
 
def gano_color(n, apuesta_color="Rojo"):
    """Devuelve True si el número coincide con el color apostado."""
    if n == 0:
        return False
    if apuesta_color == "Rojo":
        return es_rojo(n)
    else:
        return not es_rojo(n)
 
def fibonacci_n(n):
    """Retorna el n-ésimo número de Fibonacci (1-indexado, empieza en 1,1,2,3,5...)."""
    a, b = 1, 1
    for _ in range(n - 1):
        a, b = b, a + b
    return a
 
# ─────────────────────────────────────────────
# Estrategias — capital FINITO (agotar saldo)
# ─────────────────────────────────────────────
 
def martingala_finito(capital_inicial):
    saldo = capital_inicial
    apuesta = APUESTA_INICIAL
    historial_saldo = [saldo]
    historial_apuestas = [apuesta]
    historial_frsa = []          # frecuencia relativa de apuesta favorable según n
    victorias_acumuladas = 0
    tirada = 0
 
    while saldo > 0:
        apuesta_real = min(apuesta, saldo)
        n = girar_ruleta()
        gano = gano_color(n)
        tirada += 1
 
        if gano:
            saldo += apuesta_real
            victorias_acumuladas += 1
            apuesta = APUESTA_INICIAL
        else:
            saldo -= apuesta_real
            apuesta = apuesta_real * 2
 
        historial_saldo.append(saldo)
        historial_apuestas.append(apuesta_real)
        historial_frsa.append(victorias_acumuladas / tirada)
 
    return historial_saldo, historial_apuestas, historial_frsa
 
 
def dalembert_finito(capital_inicial):
    saldo = capital_inicial
    apuesta = APUESTA_INICIAL
    historial_saldo = [saldo]
    historial_apuestas = [apuesta]
    historial_frsa = []
    victorias_acumuladas = 0
    tirada = 0
 
    while saldo > 0:
        apuesta_real = min(apuesta, saldo)
        n = girar_ruleta()
        gano = gano_color(n)
        tirada += 1
 
        if gano:
            saldo += apuesta_real
            victorias_acumuladas += 1
            apuesta = max(APUESTA_INICIAL, apuesta - APUESTA_INICIAL)
        else:
            saldo -= apuesta_real
            apuesta = apuesta + APUESTA_INICIAL
 
        historial_saldo.append(saldo)
        historial_apuestas.append(apuesta_real)
        historial_frsa.append(victorias_acumuladas / tirada)
 
    return historial_saldo, historial_apuestas, historial_frsa
 
 
def fibonacci_finito(capital_inicial):
    saldo = capital_inicial
    paso = 1   # índice en la secuencia de Fibonacci
    historial_saldo = [saldo]
    historial_apuestas = []
    historial_frsa = []
    victorias_acumuladas = 0
    tirada = 0
 
    while saldo > 0:
        apuesta = fibonacci_n(paso) * APUESTA_INICIAL
        apuesta_real = min(apuesta, saldo)
        n = girar_ruleta()
        gano = gano_color(n)
        tirada += 1
 
        if gano:
            saldo += apuesta_real
            victorias_acumuladas += 1
            paso = max(1, paso - 2)
        else:
            saldo -= apuesta_real
            paso += 1
 
        historial_saldo.append(saldo)
        historial_apuestas.append(apuesta_real)
        historial_frsa.append(victorias_acumuladas / tirada)
 
    return historial_saldo, historial_apuestas, historial_frsa
 
 
def paroli_finito(capital_inicial):
    """
    Paroli: dobla la apuesta hasta 3 victorias consecutivas, luego vuelve al inicial.
    Al perder, vuelve al inicial.
    """
    saldo = capital_inicial
    apuesta = APUESTA_INICIAL
    victorias_seguidas = 0
    historial_saldo = [saldo]
    historial_apuestas = []
    historial_frsa = []
    victorias_acumuladas = 0
    tirada = 0
 
    while saldo > 0:
        apuesta_real = min(apuesta, saldo)
        n = girar_ruleta()
        gano = gano_color(n)
        tirada += 1
 
        if gano:
            saldo += apuesta_real
            victorias_acumuladas += 1
            victorias_seguidas += 1
            if victorias_seguidas >= 3:
                apuesta = APUESTA_INICIAL
                victorias_seguidas = 0
            else:
                apuesta = apuesta_real * 2
        else:
            saldo -= apuesta_real
            apuesta = APUESTA_INICIAL
            victorias_seguidas = 0
 
        historial_saldo.append(saldo)
        historial_apuestas.append(apuesta_real)
        historial_frsa.append(victorias_acumuladas / tirada)
 
    return historial_saldo, historial_apuestas, historial_frsa
 
# ─────────────────────────────────────────────
# Estrategias — capital INFINITO (n tiradas)
# ─────────────────────────────────────────────
 
def martingala_infinito(capital_inicial, n_tiradas):
    saldo = capital_inicial
    apuesta = APUESTA_INICIAL
    historial_saldo = [saldo]
    historial_apuestas = []
    historial_frsa = []
    victorias_acumuladas = 0
 
    for i in range(1, n_tiradas + 1):
        apuesta_real = apuesta
        n = girar_ruleta()
        gano = gano_color(n)
 
        if gano:
            saldo += apuesta_real
            victorias_acumuladas += 1
            apuesta = APUESTA_INICIAL
        else:
            saldo -= apuesta_real
            apuesta = apuesta_real * 2
 
        historial_saldo.append(saldo)
        historial_apuestas.append(apuesta_real)
        historial_frsa.append(victorias_acumuladas / i)
 
    return historial_saldo, historial_apuestas, historial_frsa
 
 
def dalembert_infinito(capital_inicial, n_tiradas):
    saldo = capital_inicial
    apuesta = APUESTA_INICIAL
    historial_saldo = [saldo]
    historial_apuestas = []
    historial_frsa = []
    victorias_acumuladas = 0
 
    for i in range(1, n_tiradas + 1):
        apuesta_real = apuesta
        n = girar_ruleta()
        gano = gano_color(n)
 
        if gano:
            saldo += apuesta_real
            victorias_acumuladas += 1
            apuesta = max(APUESTA_INICIAL, apuesta - APUESTA_INICIAL)
        else:
            saldo -= apuesta_real
            apuesta = apuesta + APUESTA_INICIAL
 
        historial_saldo.append(saldo)
        historial_apuestas.append(apuesta_real)
        historial_frsa.append(victorias_acumuladas / i)
 
    return historial_saldo, historial_apuestas, historial_frsa
 
 
def fibonacci_infinito(capital_inicial, n_tiradas):
    saldo = capital_inicial
    paso = 1
    historial_saldo = [saldo]
    historial_apuestas = []
    historial_frsa = []
    victorias_acumuladas = 0
 
    for i in range(1, n_tiradas + 1):
        apuesta = fibonacci_n(paso) * APUESTA_INICIAL
        n = girar_ruleta()
        gano = gano_color(n)
 
        if gano:
            saldo += apuesta
            victorias_acumuladas += 1
            paso = max(1, paso - 2)
        else:
            saldo -= apuesta
            paso += 1
 
        historial_saldo.append(saldo)
        historial_apuestas.append(apuesta)
        historial_frsa.append(victorias_acumuladas / i)
 
    return historial_saldo, historial_apuestas, historial_frsa
 
 
def paroli_infinito(capital_inicial, n_tiradas):
    saldo = capital_inicial
    apuesta = APUESTA_INICIAL
    victorias_seguidas = 0
    historial_saldo = [saldo]
    historial_apuestas = []
    historial_frsa = []
    victorias_acumuladas = 0
 
    for i in range(1, n_tiradas + 1):
        apuesta_real = apuesta
        n = girar_ruleta()
        gano = gano_color(n)
 
        if gano:
            saldo += apuesta_real
            victorias_acumuladas += 1
            victorias_seguidas += 1
            if victorias_seguidas >= 3:
                apuesta = APUESTA_INICIAL
                victorias_seguidas = 0
            else:
                apuesta = apuesta_real * 2
        else:
            saldo -= apuesta_real
            apuesta = APUESTA_INICIAL
            victorias_seguidas = 0
 
        historial_saldo.append(saldo)
        historial_apuestas.append(apuesta_real)
        historial_frsa.append(victorias_acumuladas / i)
 
    return historial_saldo, historial_apuestas, historial_frsa
 
# ─────────────────────────────────────────────
# Selección de función según estrategia y modo
# ─────────────────────────────────────────────
 
ESTRATEGIAS = {
    "m": {"nombre": "Martingala",  "finito": martingala_finito,  "infinito": martingala_infinito},
    "d": {"nombre": "D'Alembert",  "finito": dalembert_finito,   "infinito": dalembert_infinito},
    "f": {"nombre": "Fibonacci",   "finito": fibonacci_finito,   "infinito": fibonacci_infinito},
    "o": {"nombre": "Paroli",      "finito": paroli_finito,      "infinito": paroli_infinito},
}
 
# ─────────────────────────────────────────────
# Graficación
# ─────────────────────────────────────────────
 
def graficar_resultados(capital, n_tiradas, estrategia_key, modo, resultados):
    """
    resultados: lista de NUM_CORRIDAS tuplas (hist_saldo, hist_apuestas, hist_frsa)
    """
    nombre = ESTRATEGIAS[estrategia_key]["nombre"]
    modo_str = "capital infinito" if modo == "i" else "capital finito (hasta agotar)"
    titulo_base = f"{nombre} — {modo_str} — capital inicial ${capital}"
 
    # ── Figura 1: Flujo de caja (todas las corridas juntas) ──────────────
    fig1, ax1 = plt.subplots(figsize=(10, 5))
    for idx, (hist_saldo, _, _) in enumerate(resultados):
        tiradas = list(range(len(hist_saldo)))
        ax1.plot(tiradas, hist_saldo, color=COLORES_CORRIDAS[idx],
                 label=f"Corrida {idx+1}", linewidth=1.2)
    ax1.axhline(y=capital, color="black", linestyle="--", linewidth=1,
                label=f"Capital inicial (${capital})")
    ax1.set_xlabel("Número de tiradas (n)")
    ax1.set_ylabel("Capital (cc)")
    ax1.set_title(f"Flujo de caja — {titulo_base}")
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"flujo_caja_{estrategia_key}_{modo}.png", dpi=120)
    plt.show()
 
    # ── Figura 2: Frecuencia relativa de apuesta favorable según n ────────
    fig2, axes2 = plt.subplots(2, 3, figsize=(15, 8), sharey=True)
    axes2 = axes2.flatten()
    for idx, (_, _, hist_frsa) in enumerate(resultados):
        tiradas = list(range(1, len(hist_frsa) + 1))
        axes2[idx].bar(tiradas, hist_frsa, color=COLORES_CORRIDAS[idx],
                       width=0.8, alpha=0.8)
        axes2[idx].axhline(y=18/37, color="black", linestyle="--",
                           linewidth=1, label="P(ganar)=18/37≈0.486")
        axes2[idx].set_title(f"Corrida {idx+1}")
        axes2[idx].set_xlabel("n (número de tiradas)")
        axes2[idx].set_ylabel("frsa")
        axes2[idx].legend(fontsize=7)
        axes2[idx].grid(True, alpha=0.3)
    axes2[-1].set_visible(False)
    fig2.suptitle(
        f"Frecuencia relativa de apuesta favorable según n\n{titulo_base}",
        fontsize=11)
    plt.tight_layout()
    plt.savefig(f"frsa_{estrategia_key}_{modo}.png", dpi=120)
    plt.show()
 
    # ── Figura 3: Evolución de las apuestas por corrida ───────────────────
    fig3, axes3 = plt.subplots(2, 3, figsize=(15, 8))
    axes3 = axes3.flatten()
    for idx, (_, hist_apuestas, _) in enumerate(resultados):
        tiradas = list(range(1, len(hist_apuestas) + 1))
        axes3[idx].plot(tiradas, hist_apuestas, color=COLORES_CORRIDAS[idx],
                        marker="o", markersize=3, linewidth=0.8)
        axes3[idx].set_title(f"Corrida {idx+1}")
        axes3[idx].set_xlabel("Número de tiradas")
        axes3[idx].set_ylabel("Monto apostado ($)")
        axes3[idx].grid(True, alpha=0.3)
    axes3[-1].set_visible(False)
    fig3.suptitle(
        f"Evolución de las apuestas por corrida\n{titulo_base}",
        fontsize=11)
    plt.tight_layout()
    plt.savefig(f"apuestas_{estrategia_key}_{modo}.png", dpi=120)
    plt.show()
 
    # ── Resumen por consola ───────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"  Estrategia : {nombre}")
    print(f"  Modo       : {modo_str}")
    print(f"  Capital inicial : ${capital}")
    print(f"{'='*60}")
    for idx, (hist_saldo, hist_apuestas, hist_frsa) in enumerate(resultados):
        saldo_final = hist_saldo[-1]
        n = len(hist_apuestas)
        ganancia = saldo_final - capital
        frsa_final = hist_frsa[-1] if hist_frsa else 0
        bankrota = "SÍ" if saldo_final == 0 else "NO"
        print(f"  Corrida {idx+1}: tiradas={n:>4}  saldo final=${saldo_final:>8.1f}"
              f"  ganancia=${ganancia:>+8.1f}  frsa={frsa_final:.3f}"
              f"  bancarrota={bankrota}")
    print(f"{'='*60}\n")
 
 
# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────
 
def parse_args():
    parser = argparse.ArgumentParser(
        description="TP 1.2 — Simulación de estrategias de apuesta en ruleta europea"
    )
    parser.add_argument("-c", type=float, required=True,
                        help="Capital inicial del jugador")
    parser.add_argument("-n", type=int, default=50,
                        help="Número de tiradas (usado si -a i)")
    parser.add_argument("-e", type=int, default=None,
                        help="Número específico a usar en la estrategia (opcional)")
    parser.add_argument("-s", type=str, required=True, choices=["m", "d", "f", "o"],
                        help="Estrategia: m=Martingala, d=D'Alembert, f=Fibonacci, o=Paroli")
    parser.add_argument("-a", type=str, required=True, choices=["i", "f"],
                        help="Tipo de capital: i=infinito (n tiradas), f=finito (agotar saldo)")
    return parser.parse_args()
 
 
def ejecutar_corridas(capital, n_tiradas, estrategia_key, modo):
    """Ejecuta NUM_CORRIDAS corridas y devuelve sus resultados."""
    resultados = []
    func_finito   = ESTRATEGIAS[estrategia_key]["finito"]
    func_infinito = ESTRATEGIAS[estrategia_key]["infinito"]
 
    for _ in range(NUM_CORRIDAS):
        if modo == "f":
            hist_saldo, hist_apuestas, hist_frsa = func_finito(capital)
        else:
            hist_saldo, hist_apuestas, hist_frsa = func_infinito(capital, n_tiradas)
        resultados.append((hist_saldo, hist_apuestas, hist_frsa))
 
    return resultados
 
 
def main():
    args = parse_args()
    capital        = args.c
    n_tiradas      = args.n
    estrategia_key = args.s
    modo           = args.a
 
    nombre_estrategia = ESTRATEGIAS[estrategia_key]["nombre"]
    modo_str = "capital infinito" if modo == "i" else "capital finito (hasta agotar saldo)"
 
    print(f"\n{'─'*60}")
    print(f"  TP 1.2 — Ruleta Europea")
    print(f"  Estrategia : {nombre_estrategia}")
    print(f"  Modo       : {modo_str}")
    print(f"  Capital    : ${capital}")
    if modo == "i":
        print(f"  Tiradas    : {n_tiradas}")
    if args.e is not None:
        print(f"  Número ref.: {args.e}")
    print(f"{'─'*60}\n")
 
    resultados = ejecutar_corridas(capital, n_tiradas, estrategia_key, modo)
    graficar_resultados(capital, n_tiradas, estrategia_key, modo, resultados)
 
 
if __name__ == "__main__":
    main()
