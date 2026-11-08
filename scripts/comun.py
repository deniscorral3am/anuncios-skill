#!/usr/bin/env python3
"""Utilidades comunes: claves (.env), llamadas a Apify y lectura de webs. Solo librería estándar."""
import html, json, os, re, ssl, sys, urllib.error, urllib.parse, urllib.request

CARPETA = os.path.expanduser(os.environ.get("ANUNCIOS_DIR", "~/Anuncios"))
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")


def cargar_env():
    """Lee claves de las variables de entorno y, si faltan, de ./.env o ~/Anuncios/.env. Nunca las imprime."""
    for ruta in (os.path.join(os.getcwd(), ".env"), os.path.join(CARPETA, ".env")):
        if not os.path.exists(ruta):
            continue
        for linea in open(ruta, encoding="utf-8"):
            linea = linea.strip()
            if not linea or linea.startswith("#") or "=" not in linea:
                continue
            k, v = linea.split("=", 1)
            k = k.strip().removeprefix("export ").strip()
            os.environ.setdefault(k, v.strip().strip('"').strip("'"))


def clave(nombre, obligatoria=True, ayuda=""):
    cargar_env()
    v = os.environ.get(nombre, "").strip()
    if not v and obligatoria:
        sys.exit(f"FALTA_CLAVE: no encuentro {nombre}. Ponla en {CARPETA}/.env ({nombre}=...). {ayuda}")
    return v


def apify(actor, entrada, tope_usd=0.5, timeout=290):
    """Lanza un actor de Apify y devuelve los elementos del dataset. tope_usd = gasto máximo de la ejecución."""
    tok = clave("APIFY_TOKEN", ayuda="Sácala en console.apify.com → Settings → API & Integrations (cuenta gratis: 5 $/mes).")
    url = (f"https://api.apify.com/v2/acts/{actor}/run-sync-get-dataset-items"
           f"?timeout={timeout}&maxTotalChargeUsd={max(tope_usd, 0.01):.2f}")
    req = urllib.request.Request(url, data=json.dumps(entrada).encode(),
                                 headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout + 40) as r:
            d = json.load(r)
    except urllib.error.HTTPError as e:
        msg = e.read().decode(errors="ignore")[:300]
        if e.code in (401, 403):
            sys.exit(f"CLAVE_MAL: Apify no acepta la clave ({e.code}).")
        if e.code == 402 or "credit" in msg.lower() or "usage" in msg.lower():
            sys.exit(f"SIN_SALDO: se ha acabado el saldo de Apify de este mes. {msg}")
        sys.exit(f"ERROR_APIFY {e.code}: {msg}")
    if isinstance(d, dict):
        err = d.get("error", {})
        sys.exit(f"ERROR_APIFY: {err.get('type')} {err.get('message') or json.dumps(d)[:300]}")
    return d


def bajar(url, timeout=20, maximo=1_500_000):
    """Descarga una página y devuelve (url_final, html) o (url, '') si falla."""
    ctx = ssl.create_default_context()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "es-ES,es;q=0.9"})
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
            if "html" not in (r.headers.get("Content-Type") or "html"):
                return r.geturl(), ""
            raw = r.read(maximo)
            cs = r.headers.get_content_charset() or "utf-8"
            return r.geturl(), raw.decode(cs, errors="ignore")
    except Exception:
        return url, ""


def texto_visible(h):
    h = re.sub(r"(?is)<(script|style|noscript|svg|template)[^>]*>.*?</\1>", " ", h)
    h = re.sub(r"(?s)<!--.*?-->", " ", h)
    h = re.sub(r"(?i)<br\s*/?>|</(p|div|li|h\d|section|tr)>", "\n", h)
    t = html.unescape(re.sub(r"<[^>]+>", " ", h))
    t = re.sub(r"[ \t\r\f\v]+", " ", t)
    return re.sub(r"\n\s*\n+", "\n", t).strip()


def meta(h, nombre):
    m = re.search(rf'(?is)<meta[^>]+(?:name|property)=["\']{re.escape(nombre)}["\'][^>]*content=["\']([^"\']*)', h) or \
        re.search(rf'(?is)<meta[^>]+content=["\']([^"\']*)["\'][^>]*(?:name|property)=["\']{re.escape(nombre)}["\']', h)
    return html.unescape(m.group(1)).strip() if m else ""


def resumen_web(url):
    """Lo que hace falta para entender un negocio desde su web."""
    if not url.startswith("http"):
        url = "https://" + url
    final, h = bajar(url)
    if not h:
        return {"url": url, "error": "no carga"}
    tit = re.search(r"(?is)<title[^>]*>(.*?)</title>", h)
    cab = [texto_visible(x) for x in re.findall(r"(?is)<h[1-3][^>]*>(.*?)</h[1-3]>", h)]
    cab = [c for c in cab if 2 < len(c) < 160][:25]
    return {
        "url": final,
        "titulo": html.unescape(tit.group(1)).strip() if tit else "",
        "descripcion": meta(h, "description") or meta(h, "og:description"),
        "cabeceras": cab,
        "texto": texto_visible(h)[:4000],
    }


if __name__ == "__main__":
    # python3 comun.py https://tuweb.es  → resumen de la web en JSON (para deducir sector y competencia)
    if len(sys.argv) < 2:
        sys.exit("Uso: python3 comun.py https://tuweb.es")
    print(json.dumps(resumen_web(sys.argv[1]), ensure_ascii=False, indent=1))
