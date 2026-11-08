#!/usr/bin/env python3
"""CUENTA · lee tus anuncios y sus métricas de tu cuenta publicitaria de Meta (SOLO LECTURA).

Necesitas META_ACCESS_TOKEN (permiso ads_read) y el ID de tu cuenta publicitaria (act_123... o 123...).
Cómo sacarlo: README → «Conectar tu cuenta publicitaria». Este script solo hace peticiones GET: no crea, no pausa,
no cambia presupuestos. Los cambios los haces tú en el Administrador de anuncios.

Uso:
  python3 cuenta.py --cuenta act_1234567890 --dias 30 --salida ~/Anuncios/mi-cuenta
  python3 cuenta.py --comprobar                     (solo mira si el token funciona y qué cuentas ve)

Sale en --salida:
  mis-anuncios.json   cada anuncio con su texto, titular, botón, imagen, conjunto, campaña y presupuesto
  metricas.csv        gasto, impresiones, clics, CTR, CPC, CPM, resultados y coste por resultado por anuncio
                      (lo lee presupuesto.py para proponer dónde mover el dinero)
"""
import argparse, csv, json, os, sys, urllib.error, urllib.parse, urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comun import CARPETA, cargar_env, clave  # noqa: E402

VERSION = None
RESULTADOS = ["purchase", "offsite_conversion.fb_pixel_purchase", "lead", "offsite_conversion.fb_pixel_lead",
              "onsite_conversion.lead_grouped", "onsite_conversion.messaging_conversation_started_7d",
              "complete_registration", "offsite_conversion.fb_pixel_complete_registration", "schedule",
              "contact", "link_click"]


def graph(ruta, params):
    tok = clave("META_ACCESS_TOKEN", ayuda="Mira el README: «Conectar tu cuenta publicitaria» (permiso ads_read).")
    params = dict(params, access_token=tok)
    url = f"https://graph.facebook.com/{VERSION}/{ruta}?" + urllib.parse.urlencode(params)
    datos = []
    while url:
        try:
            with urllib.request.urlopen(urllib.request.Request(url), timeout=60) as r:
                d = json.load(r)
        except urllib.error.HTTPError as e:
            try:
                err = json.load(e).get("error", {})
            except Exception:
                err = {}
            cod = err.get("code")
            if cod == 190:
                sys.exit("TOKEN_MAL: Meta dice que el token no vale o ha caducado. Genera uno nuevo (README).")
            if cod in (10, 200, 294) or "permission" in str(err.get("message", "")).lower():
                sys.exit(f"SIN_PERMISO: al token le falta el permiso ads_read o acceso a esa cuenta. ({err.get('message')})")
            if cod in (4, 17, 32, 613):
                sys.exit("LIMITE: Meta ha frenado las peticiones. Espera unos minutos y vuelve a probar.")
            sys.exit(f"ERROR_META {e.code}: {err.get('message') or 'sin detalle'}")
        if "data" not in d:
            return d
        datos += d["data"]
        url = (d.get("paging") or {}).get("next")
    return datos


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return 0.0


def resultado(fila, preferido):
    acciones = {a["action_type"]: num(a["value"]) for a in fila.get("actions") or []}
    orden = [preferido] + RESULTADOS if preferido else RESULTADOS
    for t in orden:
        if acciones.get(t):
            return t, acciones[t]
    return "", 0.0


def main():
    global VERSION
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cuenta", help="ID de la cuenta publicitaria (act_123… o 123…)")
    ap.add_argument("--dias", type=int, default=30, choices=[7, 14, 30, 90])
    ap.add_argument("--resultado", default="", help="acción que cuenta como resultado (p. ej. lead, purchase); si no, la deduce")
    ap.add_argument("--salida", default=os.path.join(CARPETA, "mi-cuenta"))
    ap.add_argument("--comprobar", action="store_true")
    a = ap.parse_args()
    cargar_env()
    VERSION = os.environ.get("META_API_VERSION", "v23.0")

    if a.comprobar:
        yo = graph("me", {"fields": "id,name"})
        cuentas = graph("me/adaccounts", {"fields": "account_id,name,currency,account_status", "limit": 50})
        print(f"Token OK ({yo.get('name')}). Cuentas que ve:")
        for c in cuentas:
            print(f"  act_{c['account_id']} · {c.get('name')} · {c.get('currency')} · estado {c.get('account_status')}")
        return
    cuenta = a.cuenta or os.environ.get("META_AD_ACCOUNT_ID", "")
    if not cuenta:
        sys.exit("FALTA_CUENTA: dime --cuenta act_123… (o pon META_AD_ACCOUNT_ID en ~/Anuncios/.env). "
                 "Con --comprobar ves las cuentas que tiene tu token.")
    cuenta = cuenta if cuenta.startswith("act_") else f"act_{cuenta}"
    out = os.path.expanduser(a.salida)
    preset = {7: "last_7d", 14: "last_14d", 30: "last_30d", 90: "last_90d"}[a.dias]
    ads = graph(f"{cuenta}/ads", {
        "fields": "id,name,effective_status,adset{id,name,daily_budget,lifetime_budget,optimization_goal},"
                  "campaign{id,name,objective,daily_budget,lifetime_budget},"
                  "creative{title,body,call_to_action_type,image_url,thumbnail_url,object_story_spec,asset_feed_spec}",
        "limit": 100, "effective_status": json.dumps(["ACTIVE", "PAUSED", "ADSET_PAUSED", "CAMPAIGN_PAUSED"])})
    met = graph(f"{cuenta}/insights", {
        "level": "ad", "date_preset": preset, "limit": 200,
        "fields": "ad_id,ad_name,adset_id,adset_name,campaign_id,campaign_name,spend,impressions,reach,frequency,"
                  "clicks,inline_link_clicks,ctr,cpc,cpm,actions,purchase_roas"})

    os.makedirs(out, exist_ok=True)
    limpio = []
    for x in ads:
        cr = x.get("creative") or {}
        oss = cr.get("object_story_spec") or {}
        ld = oss.get("link_data") or oss.get("video_data") or {}
        afs = cr.get("asset_feed_spec") or {}
        texto = cr.get("body") or ld.get("message") or ((afs.get("bodies") or [{}])[0].get("text"))
        titulo = cr.get("title") or ld.get("name") or ld.get("title") or ((afs.get("titles") or [{}])[0].get("text"))
        aset, camp = x.get("adset") or {}, x.get("campaign") or {}
        limpio.append({
            "id": x["id"], "nombre": x.get("name"), "estado": x.get("effective_status"), "texto": texto, "titulo": titulo,
            "boton": cr.get("call_to_action_type") or (ld.get("call_to_action") or {}).get("type"),
            "imagen_url": cr.get("image_url") or cr.get("thumbnail_url"),
            "conjunto": aset.get("name"), "conjunto_id": aset.get("id"),
            "presupuesto_diario_conjunto": num(aset.get("daily_budget")) / 100 or None,
            "campana": camp.get("name"), "objetivo": camp.get("objective"),
            "presupuesto_diario_campana": num(camp.get("daily_budget")) / 100 or None,
        })
    json.dump(limpio, open(os.path.join(out, "mis-anuncios.json"), "w"), ensure_ascii=False, indent=1)

    with open(os.path.join(out, "metricas.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["anuncio_id", "anuncio", "conjunto", "campana", "gasto", "impresiones", "alcance", "frecuencia",
                    "clics_enlace", "ctr", "cpc", "cpm", "tipo_resultado", "resultados", "coste_por_resultado", "roas"])
        for m in met:
            tipo, n = resultado(m, a.resultado)
            g = num(m.get("spend"))
            roas = num((m.get("purchase_roas") or [{}])[0].get("value")) if m.get("purchase_roas") else ""
            w.writerow([m.get("ad_id"), m.get("ad_name"), m.get("adset_name"), m.get("campaign_name"), g,
                        m.get("impressions"), m.get("reach"), m.get("frequency"), m.get("inline_link_clicks"),
                        m.get("ctr"), m.get("cpc"), m.get("cpm"), tipo, n, round(g / n, 2) if n else "", roas])
    print(f"Listo: {len(limpio)} anuncios y {len(met)} filas de métricas ({preset}) → {out}/")


if __name__ == "__main__":
    main()
