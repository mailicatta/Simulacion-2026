"""
TP 1.1 - Simulación de una Ruleta

Uso:
    python TP1_1.py -c <corridas> -n <tiradas> -e <numero_elegido>
 
Ejemplo:
    python TP1_1.py -c 10 -n 1000 -e 18
"""
 
import argparse
import random
import numpy as np
import matplotlib.pyplot as plt
 
#  Valores esperados teóricos (ruleta europea 0-36) 
VPE = 18            # valor promedio esperado
VVE = 114           # varianza esperada
VDE = np.sqrt(VVE)  # desvío esperado ≈ 10.6771
FRE = 1 / 37        # frecuencia relativa esperada ≈ 0.0270
 
#  Variable global 
conjuntoValores = []   # lista de corridas; cada corrida es una lista de resultados
 
 
# 1. GENERACIÓN DE VALORES

def simular(tiradas, corridas):
    for _ in range(corridas):
        corrida = []
        for _ in range(tiradas):
            corrida.append(random.randint(0, 36))
        conjuntoValores.append(corrida)
 
# 2. GRÁFICA — Frecuencia Relativa del número elegido vs n

def graficaFrecuenciaRelativa(tiradas, corridas, numero_elegido):
    for c in range(corridas):
        x = []; y = []
        aciertos = 0
        for i in range(tiradas):
            if conjuntoValores[c][i] == numero_elegido:
                aciertos += 1
            x.append(i + 1)
            y.append(aciertos / (i + 1))
        plt.plot(x, y, alpha=0.75)
 
    plt.axhline(y=FRE, color="blue", linewidth=2, linestyle="--",
                label=f"fre = {FRE:.4f}")
    plt.xlabel("n (número de tiradas)")
    plt.ylabel("fr (frecuencia relativa)")
    plt.title(f"Frecuencia Relativa del número {numero_elegido} — {corridas} corridas")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(f"fr_numero{numero_elegido}.png", dpi=150)
    print(f"  → Guardada: fr_numero{numero_elegido}.png")
    plt.show()
 
 
# 3. GRÁFICA — Valor Promedio acumulado vs n

def graficaPromedio(tiradas, corridas):
    for c in range(corridas):
        x = []; y = []
        suma = 0
        for i in range(tiradas):
            suma += conjuntoValores[c][i]
            x.append(i + 1)
            y.append(suma / (i + 1))
        plt.plot(x, y, alpha=0.75)
 
    plt.axhline(y=VPE, color="blue", linewidth=2, linestyle="--",
                label=f"vpe = {VPE}")
    plt.xlabel("n (número de tiradas)")
    plt.ylabel("vp (valor promedio)")
    plt.title(f"Valor Promedio acumulado — {corridas} corridas")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig("vp_corridas.png", dpi=150)
    print("  → Guardada: vp_corridas.png")
    plt.show()
 
# 4. GRÁFICA — Desvío Estándar acumulado vs n

def graficaDesvio(tiradas, corridas):
    for c in range(corridas):
        x = []; y = []; vals = []
        for i in range(tiradas):
            vals.append(conjuntoValores[c][i])
            x.append(i + 1)
            y.append(np.std(vals))
        plt.plot(x, y, alpha=0.75)
 
    plt.axhline(y=VDE, color="blue", linewidth=2, linestyle="--",
                label=f"vde = {VDE:.4f}")
    plt.xlabel("n (número de tiradas)")
    plt.ylabel("vd (desvío estándar)")
    plt.title(f"Desvío Estándar acumulado — {corridas} corridas")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig("vd_corridas.png", dpi=150)
    print("  → Guardada: vd_corridas.png")
    plt.show()
 

# 5. GRÁFICA — Varianza acumulada vs n

def graficaVarianza(tiradas, corridas):
    for c in range(corridas):
        x = []; y = []; vals = []
        for i in range(tiradas):
            vals.append(conjuntoValores[c][i])
            x.append(i + 1)
            y.append(np.var(vals))
        plt.plot(x, y, alpha=0.75)
 
    plt.axhline(y=VVE, color="blue", linewidth=2, linestyle="--",
                label=f"vve = {VVE}")
    plt.xlabel("n (número de tiradas)")
    plt.ylabel("vv (varianza)")
    plt.title(f"Varianza acumulada — {corridas} corridas")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig("vv_corridas.png", dpi=150)
    print("  → Guardada: vv_corridas.png")
    plt.show()
 

# 6. GRÁFICA — Promedio final de cada corrida (promedio de promedios)

def graficaPromedioDeProm(corridas):
    x = []; y = []
    for c in range(corridas):
        x.append(c + 1)
        y.append(np.mean(conjuntoValores[c]))
 
    plt.plot(x, y, marker="o", color="red", linewidth=2,
             label="vp final por corrida")
    plt.axhline(y=VPE, color="blue", linewidth=2, linestyle="--",
                label=f"vpe = {VPE}")
    plt.axhline(y=np.mean(y), color="green", linewidth=1.5, linestyle="-.",
                label=f"media entre corridas = {np.mean(y):.4f}")
    plt.xlabel("Número de corrida")
    plt.ylabel("Promedio final")
    plt.title("Promedio final de cada corrida\n"
              "(variabilidad entre experimentos independientes)")
    plt.xticks(x)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig("promedio_de_promedios.png", dpi=150)
    print("  → Guardada: promedio_de_promedios.png")
    plt.show()
 
 
# 7. GRÁFICA — Nube de puntos

def graficaNubePuntos(tiradas, corridas, numero_elegido):
    for c in range(corridas):
        x = []; y = []
        for i in range(tiradas):
            x.append(i + 1)
            y.append(conjuntoValores[c][i])
        plt.scatter(x, y, alpha=0.2, s=4)
 
    plt.axhline(y=numero_elegido, color="red", linewidth=1.5, linestyle="--",
                label=f"Número elegido: {numero_elegido}")
    plt.xlabel("n (número de tirada)")
    plt.ylabel("Valor obtenido")
    plt.title("Nube de puntos — Resultados brutos\n"
              "(ausencia de patrones confirma aleatoriedad)")
    plt.yticks(range(0, 37, 5))
    plt.legend()
    plt.grid(True, alpha=0.2)
    plt.savefig("nube_puntos.png", dpi=150)
    print("  → Guardada: nube_puntos.png")
    plt.show()
 
# 8. GRÁFICA — Histograma de frecuencias absolutas

def graficaHistograma(tiradas, corridas, numero_elegido):
    todos = []
    for c in range(corridas):
        todos.extend(conjuntoValores[c])
 
    plt.hist(todos, bins=range(0, 38), align="left",
             color="#2A9D8F", edgecolor="white", rwidth=0.7)
    plt.axhline(y=len(todos) / 37, color="red", linewidth=2, linestyle="--",
                label=f"Frecuencia esperada = {len(todos)/37:.1f}")
    plt.axvline(x=numero_elegido, color="orange", linewidth=2, linestyle=":",
                label=f"Número elegido: {numero_elegido}")
    plt.xlabel("Número de ruleta")
    plt.ylabel("Frecuencia absoluta")
    plt.title("Distribución de frecuencias absolutas — todas las corridas\n"
              "(distribución uniforme: todos los números deben aparecer similar cantidad de veces)")
    plt.xticks(range(0, 37))
    plt.legend()
    plt.grid(True, axis="y", alpha=0.3)
    plt.savefig("histograma.png", dpi=150)
    print("  → Guardada: histograma.png")
    plt.show()

 
# RESUMEN EN CONSOLA

def resumen(tiradas, corridas, numero_elegido):
    sep = "─" * 70
    print(f"\n{sep}")
    print("  RESUMEN — Ruleta Europea (0 al 36)")
    print(f"{sep}")
    print(f"  Número elegido: {numero_elegido} | Tiradas: {tiradas} | Corridas: {corridas}")
    print(f"{sep}")
    print(f"  {'Corrida':>8} | {'fr final':>10} | {'vp final':>10} | "
          f"{'vd final':>10} | {'vv final':>10}")
    print(f"  {'-'*8}-+-{'-'*10}-+-{'-'*10}-+-{'-'*10}-+-{'-'*10}")
 
    vp_finales = []; fr_finales = []
    for c in range(corridas):
        vals = conjuntoValores[c]
        aciertos = sum(1 for v in vals if v == numero_elegido)
        fr = aciertos / tiradas
        vp = np.mean(vals)
        vd = np.std(vals)
        vv = np.var(vals)
        fr_finales.append(fr)
        vp_finales.append(vp)
        print(f"  {c+1:>8} | {fr:>10.4f} | {vp:>10.4f} | {vd:>10.4f} | {vv:>10.4f}")
 
    print(f"{sep}")
    print(f"  {'ESPERADO':>8} | {FRE:>10.4f} | {VPE:>10.4f} | {VDE:>10.4f} | {VVE:>10.4f}")
    print(f"{sep}")
    print(f"\n  Promedios finales entre corridas:")
    print(f"    fr promedio : {np.mean(fr_finales):.4f}  (esperado: {FRE:.4f})")
    print(f"    vp promedio : {np.mean(vp_finales):.4f}  (esperado: {VPE:.4f})")
    print(f"{sep}\n")
 
# MAIN
def main():
    parser = argparse.ArgumentParser(
        description="TP1.1 — Simulación de Ruleta Europea — UTN FRRO"
    )
    parser.add_argument("-c", "--corridas", type=int, default=10,
                        help="Número de corridas (default: 10)")
    parser.add_argument("-n", "--tiradas",  type=int, default=1000,
                        help="Tiradas por corrida (default: 1000)")
    parser.add_argument("-e", "--elegido",  type=int, default=18,
                        help="Número elegido 0-36 (default: 7)")
    args = parser.parse_args()
 
    tiradas        = args.tiradas
    corridas       = args.corridas
    numero_elegido = args.elegido
 
    if not (0 <= numero_elegido <= 36):
        print("Error: el número elegido debe estar entre 0 y 36.")
        return
 
    print(f"\n{'═'*70}")
    print("  TP 1.1 — Simulación de Ruleta Europea — UTN FRRO")
    print(f"{'═'*70}")
    print(f"  Corridas: {corridas}  |  Tiradas: {tiradas}  |  Número elegido: {numero_elegido}")
    print(f"{'═'*70}\n")
 
    # Generar todos los valores aleatorios
    simular(tiradas, corridas)
 
    # Gráficas
    print("  [1] Frecuencia Relativa del número elegido...")
    graficaFrecuenciaRelativa(tiradas, corridas, numero_elegido)
 
    print("  [2] Valor Promedio acumulado...")
    graficaPromedio(tiradas, corridas)
 
    print("  [3] Desvío Estándar acumulado...")
    graficaDesvio(tiradas, corridas)
 
    print("  [4] Varianza acumulada...")
    graficaVarianza(tiradas, corridas)
 
    print("  [5] Promedio de promedios por corrida...")
    graficaPromedioDeProm(corridas)
 
    print("  [6] Nube de puntos (resultados brutos)...")
    graficaNubePuntos(tiradas, corridas, numero_elegido)
 
    print("  [7] Histograma de distribución...")
    graficaHistograma(tiradas, corridas, numero_elegido)

    # Resumen en consola
    resumen(tiradas, corridas, numero_elegido)
 
if __name__ == "__main__":
    main()