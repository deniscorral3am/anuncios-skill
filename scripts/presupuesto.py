#!/usr/bin/env python3
"""PRESUPUESTO · propone dónde mover el dinero según tus métricas reales.

Lee metricas.csv (el de cuenta.py o una exportación del Administrador de anuncios con columnas parecidas:
anuncio, gasto, resultados, impresiones, clics_enlace…) y clasifica cada anuncio:

  ESCALAR   coste por resultado ≤ 80 % de tu media y con datos suficientes  → subir un 20 % (no más de golpe)
  MANTENER  cerca de tu media                                              → no tocar, dejar que aprenda
  RECORTAR  coste por resultado ≥ 150 % de tu media                        → bajar o mover su dinero
  APAGAR    ha gastado ≥ 2 veces tu coste objetivo sin ningún resultado     → pausar y reutilizar el dinero
  POCOS DATOS  aún no ha gastado lo suficiente para opinar                  → esperar

Uso:
  python3 presupuesto.py --metricas ~/Anuncios/mi-cuenta/metricas.csv [--objetivo 15] [--salida reparto.md]

No cambia nada en tu cuenta: te deja un informe para que decidas tú.
"""
import argparse, csv, os, sys

ALIAS = {"anuncio": ["anuncio", "ad_name", "nombre del anuncio", "ad name"],
         "gasto": ["gasto", "spend", "importe gastado (eur)", "importe gastado", "amount spent"],
         "resultados": ["resultados", "results", "conversiones"],
         "impresiones": ["impresiones", "impressions"],
         "clics": ["clics_enlace", "clics en el enlace", "link clicks", "clicks", "clics"]}


def col(fila, nombre):
    claves = {k.strip().lower(): v for k, v in fila.items()}
    for a in ALIAS[nombre]:
        if a in claves and claves[a] not in (None, ""):
            v = str(claves[a]).replace("€", "").strip()
            if nombre == "anuncio":
                return v
            v = v.replace(".", "").replace(",", ".") if v.count(",") == 1 and v.count(".") <= 1 and "," in v[-3:] else v
            try:
                return float(v)
            except ValueError:
                return 0.0
    return "" if nombre == "anuncio" else 0.0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--metricas", required=True)
    ap.add_argument("--objetivo", type=float, default=0, help="coste por resultado que te sale rentable (€). Si no, tu media")
    ap.add_argument("--salida", default="")
    a = ap.parse_args()
    filas = list(csv.DictReader(open(os.path.expanduser(a.metricas), encoding="utf-8-sig")))
    ads = []
    for f in filas:
        x = {k: col(f, k) for k in ALIAS}
        if x["gasto"] > 0:
            ads.append(x)
    if not ads:
        sys.exit("SIN_DATOS: no hay anuncios con gasto en ese CSV.")
    total_g = sum(x["gasto"] for x in ads)
    total_r = sum(x["resultados"] for x in ads)
    media = total_g / total_r if total_r else None
    obj = a.objetivo or media
    if not obj:
        sys.exit("SIN_RESULTADOS: ningún anuncio tiene resultados todavía. Dime --objetivo (coste por resultado que te vale).")

    for x in ads:
        x["cpr"] = x["gasto"] / x["resultados"] if x["resultados"] else None
        x["ctr"] = 100 * x["clics"] / x["impresiones"] if x["impresiones"] else None
        if not x["resultados"]:
            x["accion"] = "APAGAR" if x["gasto"] >= 2 * obj else "POCOS DATOS"
        elif x["gasto"] < obj and x["resultados"] < 3:
            x["accion"] = "POCOS DATOS"
        elif x["cpr"] <= 0.8 * obj:
            x["accion"] = "ESCALAR"
        elif x["cpr"] >= 1.5 * obj:
            x["accion"] = "RECORTAR"
        else:
            x["accion"] = "MANTENER"
    liberado = sum(x["gasto"] for x in ads if x["accion"] == "APAGAR") + \
        sum(x["gasto"] * 0.5 for x in ads if x["accion"] == "RECORTAR")
    escalar = [x for x in ads if x["accion"] == "ESCALAR"]
    orden = {"ESCALAR": 0, "MANTENER": 1, "POCOS DATOS": 2, "RECORTAR": 3, "APAGAR": 4}
    ads.sort(key=lambda x: (orden[x["accion"]], x["cpr"] or 9e9))

    L = ["# Reparto de presupuesto (propuesta)", "",
         f"Gasto analizado: {total_g:.2f} € · resultados: {total_r:g} · coste medio por resultado: "
         + (f"{media:.2f} €" if media else "sin resultados") + f" · objetivo usado: {obj:.2f} €"
         + ("" if a.objetivo else " (tu media)"), "",
         "| Acción | Anuncio | Gasto | Resultados | Coste/resultado | CTR |", "|---|---|---|---|---|---|"]
    for x in ads:
        cpr = f"{x['cpr']:.2f} €" if x["cpr"] else "-"
        ctr = f"{x['ctr']:.2f} %" if x["ctr"] is not None else "-"
        L.append(f"| {x['accion']} | {x['anuncio']} | {x['gasto']:.2f} € | {x['resultados']:g} | {cpr} | {ctr} |")
    L += ["", "## Qué haría", ""]
    if escalar:
        L.append(f"- Sube un 20 % el presupuesto de: {', '.join(x['anuncio'] for x in escalar)}. Espera 3-4 días antes del siguiente cambio.")
    if liberado:
        L.append(f"- Pausar los APAGAR y recortar a la mitad los RECORTAR libera unos {liberado:.0f} € por cada periodo como este"
                 + (" para los ESCALAR." if escalar else ". Úsalos para probar 2-3 creatividades nuevas con los patrones ganadores."))
    if not escalar and not liberado:
        L.append("- Nada claro que mover: deja que los anuncios acumulen datos y prueba creatividades nuevas.")
    L += ["- No cambies más de un 20-30 % de golpe: Meta vuelve a la fase de aprendizaje.",
          "- Esto mira el coste por resultado. Si sabes cuánto vale cada resultado (ticket, % de cierre), díselo a Claude y lo afina."]
    txt = "\n".join(L) + "\n"
    if a.salida:
        open(os.path.expanduser(a.salida), "w").write(txt)
        print(f"Listo → {a.salida}")
    print(txt)


if __name__ == "__main__":
    main()
