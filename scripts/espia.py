#!/usr/bin/env python3
"""ESPÍA · saca los anuncios activos de tu sector y de tu competencia de la Biblioteca de anuncios de Meta
(Facebook + Instagram) y los ordena por señal de ganador.

Usa el actor de Apify curious_coder/facebook-ads-library-scraper (≈ 0,00075 $ por anuncio: 1.000 anuncios < 1 $).
Solo lee datos públicos: lo mismo que verías en facebook.com/ads/library.

Uso:
  python3 espia.py --palabra "fisioterapia" --palabra "fisioterapeuta valencia" --pais ES --max 20 --salida ~/Anuncios/espia
  python3 espia.py --competidor "Nombre de su página" --competidor https://www.facebook.com/supagina --max 20
  python3 espia.py --rehacer --salida ~/Anuncios/espia      (rehace el informe sin volver a gastar)

Sale en --salida:
  crudo.json      lo que devuelve Apify, tal cual
  anuncios.json   un anuncio por elemento, limpio y con la señal calculada
  informe.md      ranking de ganadores, quién anuncia más, formatos, botones y patrones de texto
  img/            (con --imagenes) la imagen o portada de cada anuncio del top
"""
import argparse, datetime as dt, hashlib, json, os, re, sys, urllib.parse, urllib.request
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comun import CARPETA, apify  # noqa: E402

ACTOR = "curious_coder~facebook-ads-library-scraper"
PRECIO = 0.00075
LIB = "https://www.facebook.com/ads/library/"
BOTONES = {"Learn more": "Más información", "Send WhatsApp message": "Enviar WhatsApp", "Book now": "Reservar",
           "Sign up": "Registrarte", "Shop now": "Comprar", "Send message": "Enviar mensaje", "Contact us": "Contactar",
           "Call now": "Llamar", "Get quote": "Pedir presupuesto", "Apply now": "Solicitar", "Watch more": "Ver más",
           "Download": "Descargar", "Get offer": "Ver oferta", "Subscribe": "Suscribirte", "Book Now": "Reservar",
           "Visit Instagram profile": "Ir al perfil de Instagram", "Order now": "Pedir ya", "Get directions": "Cómo llegar",
           "Request time": "Pedir cita", "Get access": "Acceder", "See details": "Ver detalles", "Learn More": "Más información", "No button": "Sin botón"}


def url_busqueda(q, pais):
    return LIB + "?" + urllib.parse.urlencode(dict(active_status="active", ad_type="all", country=pais, q=q,
                                                   search_type="keyword_unordered", media_type="all"))


def url_pagina(pid, pais):
    return LIB + "?" + urllib.parse.urlencode(dict(active_status="active", ad_type="all", country=pais,
                                                   view_all_page_id=pid, search_type="page", media_type="all"))


def normal(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower().translate(str.maketrans("áéíóúüñ", "aeiouun")))


LEIDOS = [0]  # anuncios cobrados en esta ejecución (incluye las búsquedas para encontrar páginas)


def pedir(urls, maximo):
    tope = max(0.05, len(urls) * maximo * PRECIO * 2)
    items = apify(ACTOR, {"urls": [{"url": u} for u in urls], "count": maximo, "scrapeAdDetails": False,
                         "scrapePageAds.activeStatus": "active", "period": ""}, tope_usd=tope)
    LEIDOS[0] += len(items)
    return items


def resolver(comp, pais):
    """Nombre de página → URL de sus anuncios (busca por palabra y se queda con la página que más se parece)."""
    c = comp.strip()
    if "facebook.com/ads/library" in c or "facebook.com/" in c:
        return c
    if c.isdigit():
        return url_pagina(c, pais)
    ads = pedir([url_busqueda(c, pais)], 15)
    n, cand = normal(c), Counter()
    for a in ads:
        pn = normal(a.get("page_name") or (a.get("snapshot") or {}).get("page_name"))
        if pn and (n in pn or pn in n):
            cand[(a.get("page_id"), a.get("page_name"))] += 1
    if not cand:
        print(f"  «{c}»: no aparece ninguna página con ese nombre con anuncios activos en {pais} "
              "(o no anuncia ahora, o su página se llama distinto: pasa la URL de su Facebook). Salen: "
              f"{sorted({a.get('page_name') for a in ads if a.get('page_name')})[:10]}")
        return None
    (pid, nombre), _ = cand.most_common(1)[0]
    print(f"  «{c}» → página «{nombre}» (ID {pid})")
    return url_pagina(pid, pais)


def dias(a):
    ts = a.get("start_date")
    if not ts:
        return None
    ini = dt.datetime.fromtimestamp(int(ts), dt.timezone.utc)
    return max(0, (dt.datetime.now(dt.timezone.utc) - ini).days)


def limpiar(a, origen):
    s = a.get("snapshot") or {}
    cards = s.get("cards") or []
    body = ((s.get("body") or {}).get("text") or "").strip()
    if (not body or "{{" in body) and cards:
        body = (cards[0].get("body") or "").strip()
    titulo = s.get("title") or ""
    if (not titulo or "{{" in titulo) and cards:
        titulo = cards[0].get("title") or ""
    imgs, vids = s.get("images") or [], s.get("videos") or []
    img = (imgs[0].get("original_image_url") or imgs[0].get("resized_image_url")) if imgs else None
    if not img and vids:
        img = vids[0].get("video_preview_image_url")
    if not img and cards:
        img = cards[0].get("original_image_url") or cards[0].get("video_preview_image_url")
    boton = s.get("cta_text") or (cards[0].get("cta_text") if cards else None) or ""
    aid = str(a.get("ad_archive_id"))
    return {
        "id": aid, "pagina": a.get("page_name") or s.get("page_name"), "pagina_id": a.get("page_id"),
        "seguidores_pagina": s.get("page_like_count"), "inicio": (a.get("start_date_formatted") or "")[:10],
        "dias_activo": dias(a), "variantes": a.get("collation_count") or 1,
        "formato": {"DCO": "dinámico (varias versiones)", "VIDEO": "vídeo", "IMAGE": "imagen",
                    "CAROUSEL": "carrusel", "DPA": "catálogo"}.get(s.get("display_format"), s.get("display_format")),
        "texto": body, "titulo": titulo, "boton": BOTONES.get(boton, boton), "destino": s.get("link_url") or
        (cards[0].get("link_url") if cards else None), "plataformas": a.get("publisher_platform") or [],
        "tarjetas": len(cards), "imagen_url": img,
        "video_url": (vids[0].get("video_hd_url") or vids[0].get("video_sd_url")) if vids else None,
        "enlace": f"{LIB}?id={aid}", "busqueda": origen, "total_en_busqueda": a.get("total"),
    }


def puntuar(x, repes, por_pagina):
    """Señal de ganador desde fuera (el rendimiento real no es público): lo que el anunciante SIGUE pagando."""
    d = x["dias_activo"] or 0
    p = 4 if d >= 90 else 3 if d >= 60 else 2 if d >= 30 else 1 if d >= 14 else 0
    p += 2 if x["variantes"] >= 5 else 1 if x["variantes"] >= 2 else 0
    p += 1 if repes >= 3 else 0          # mismo texto en varios anuncios = lo están escalando
    p += 1 if por_pagina >= 5 else 0     # anunciante que invierte en serio
    x.update(repeticiones=repes, anuncios_de_la_pagina=por_pagina, puntos=p,
             senal=("Ganador probado (meses pagándolo)" if d >= 60 else "Lo sigue pagando" if d >= 30
                    else "En prueba" if d >= 14 else "Recién lanzado"))
    return x


def patrones(ads):
    """Pistas rápidas de cómo escriben los que más aguantan (Claude saca el resto leyendo los textos)."""
    top = [x for x in ads if x["texto"] and x["puntos"] >= 2] or [x for x in ads if x["texto"]]
    if not top:
        return []
    n = len(top)
    largos = sorted(len(x["texto"].split()) for x in top)
    reglas = [
        ("Empiezan con pregunta", r"^\s*¿"),
        ("Mencionan precio, descuento o gratis", r"€|gratis|descuento|%|oferta|promo"),
        ("Hablan de dolor o problema", r"dolor|lesi|molest|problema|cansad|estrés|miedo"),
        ("Dan prueba (años, pacientes, reseñas, casos)", r"años|pacientes|clientes|reseñas|opiniones|casos|\+\d"),
        ("Urgencia o plazas limitadas", r"plazas|últim|solo hasta|hoy|limitad"),
        ("Piden escribir por WhatsApp o mensaje", r"whatsapp|escríbe|mensaje|\bdm\b"),
        ("Usan emojis", "[\U0001F300-\U0001FAFF\u2600-\u27BF]"),
    ]
    out = [f"Textos analizados: {n} (los de más señal). Longitud mediana: {largos[len(largos) // 2]} palabras."]
    for nombre, rx in reglas:
        c = sum(1 for x in top if re.search(rx, x["texto"], re.I))
        out.append(f"{nombre}: {c}/{n}")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--palabra", action="append", default=[], help="búsqueda por palabra clave (todo el sector)")
    ap.add_argument("--competidor", action="append", default=[], help="nombre, URL o ID de su página de Facebook")
    ap.add_argument("--pais", default="ES")
    ap.add_argument("--max", type=int, default=20, help="anuncios como mucho por búsqueda (gasta poco: 20)")
    ap.add_argument("--salida", default=os.path.join(CARPETA, "espia"))
    ap.add_argument("--imagenes", action="store_true", help="descarga la imagen/portada de los 15 mejores")
    ap.add_argument("--rehacer", action="store_true", help="rehace el informe con crudo.json sin gastar")
    a = ap.parse_args()
    a.salida = os.path.expanduser(a.salida)
    os.makedirs(a.salida, exist_ok=True)
    f_crudo = os.path.join(a.salida, "crudo.json")

    if a.rehacer:
        crudo = json.load(open(f_crudo))
    else:
        if not a.palabra and not a.competidor:
            sys.exit("Dime al menos una --palabra o un --competidor.")
        busquedas = [(f"palabra «{p}»", url_busqueda(p, a.pais)) for p in a.palabra]
        for c in a.competidor:
            u = resolver(c, a.pais)
            if u:
                busquedas.append((f"competidor «{c}»", u))
        crudo = []
        for nombre, u in busquedas:  # una a una: así el límite es por búsqueda
            print(f"Biblioteca de anuncios · {nombre} · hasta {a.max} anuncios…")
            items = pedir([u], a.max)
            for it in items:
                it["_origen"] = nombre
            crudo += items
        json.dump(crudo, open(f_crudo, "w"), ensure_ascii=False)

    vistos, ads = set(), []
    for r in crudo:
        if r.get("ad_archive_id") and r["ad_archive_id"] not in vistos:
            vistos.add(r["ad_archive_id"])
            ads.append(limpiar(r, r.get("_origen", "")))
    if not ads:
        sys.exit("SIN_ANUNCIOS: la búsqueda no ha devuelto anuncios activos. Prueba otra palabra o el nombre exacto de la página.")

    clave = lambda x: (x["pagina"], hashlib.md5(normal(x["texto"])[:300].encode()).hexdigest())
    rep = Counter(clave(x) for x in ads if x["texto"])
    pag = Counter(x["pagina"] for x in ads)
    ads = [puntuar(x, rep.get(clave(x), 1) if x["texto"] else 1, pag[x["pagina"]]) for x in ads]
    ads.sort(key=lambda x: (-x["puntos"], -(x["dias_activo"] or 0)))

    if a.imagenes:
        os.makedirs(os.path.join(a.salida, "img"), exist_ok=True)
        for x in ads[:15]:
            if x["imagen_url"]:
                ruta = os.path.join(a.salida, "img", f"{x['id']}.jpg")
                if os.path.exists(ruta):
                    x["imagen"] = f"img/{x['id']}.jpg"
                    continue
                try:
                    req = urllib.request.Request(x["imagen_url"], headers={"User-Agent": "Mozilla/5.0"})
                    open(ruta, "wb").write(urllib.request.urlopen(req, timeout=30).read())
                    x["imagen"] = f"img/{x['id']}.jpg"
                except Exception:
                    pass

    hoy = dt.date.today().isoformat()
    json.dump({"fecha": hoy, "pais": a.pais, "palabras": a.palabra, "competidores": a.competidor,
               "total": len(ads), "anuncios": ads}, open(os.path.join(a.salida, "anuncios.json"), "w"),
              ensure_ascii=False, indent=1)

    L = [f"# Espía de anuncios · {hoy} · país {a.pais}", "",
         f"Búsquedas: {', '.join(sorted({x['busqueda'] for x in ads}))}. Anuncios únicos leídos: {len(ads)}.", ""]
    totales = {x["busqueda"]: x["total_en_busqueda"] for x in ads if x.get("total_en_busqueda")}
    if totales:
        L.append("Anuncios activos que la biblioteca dice tener en cada búsqueda (tamaño del sector): " +
                 ", ".join(f"{k}: {v}" for k, v in totales.items()) + ".")
        L.append("")
    L += ["> La señal de ganador es lo que se ve desde fuera: cuántos días lleva activo, cuántas variantes tiene y si repite",
          "> el mismo texto. Nadie paga meses un anuncio que no le trae clientes. El gasto y los resultados no son públicos.", "",
          "## Top de anuncios por señal de ganador", ""]
    ya = set()
    n = 0
    for x in ads:
        k = clave(x) if x["texto"] else x["id"]
        if k in ya:
            continue
        ya.add(k)
        n += 1
        if n > 15:
            break
        t = re.sub(r"\s+", " ", x["texto"])[:400]
        L += [f"### {n}. {x['pagina']} · {x['senal']} · {x['puntos']} puntos",
              f"- {x['dias_activo']} días activo (desde {x['inicio']}) · {x['variantes']} variantes · mismo texto en "
              f"{x['repeticiones']} anuncios · {x['anuncios_de_la_pagina']} anuncios de esta página en la muestra",
              f"- Formato: {x['formato']} · Botón: «{x['boton']}» · Plataformas: {', '.join(x['plataformas']).lower()}",
              f"- Titular: {x['titulo'] or '(sin titular)'}",
              f"- Destino: {x['destino'] or '-'}",
              f"- Ver: {x['enlace']}" + (f" · imagen: {x['imagen']}" if x.get("imagen") else ""),
              f"> {t or '(sin texto)'}", ""]
    L += ["## Quién anuncia más", "", "| Página | Anuncios | +30 días | Más antiguo | Formatos |", "|---|---|---|---|---|"]
    por = defaultdict(list)
    for x in ads:
        por[x["pagina"]].append(x)
    for p, xs in sorted(por.items(), key=lambda kv: (-len(kv[1]), -max(y["dias_activo"] or 0 for y in kv[1])))[:15]:
        fm = Counter(y["formato"] for y in xs).most_common(2)
        L.append(f"| {p} | {len(xs)} | {sum((y['dias_activo'] or 0) >= 30 for y in xs)} | "
                 f"{max(y['dias_activo'] or 0 for y in xs)} días | {', '.join(f'{f} ×{c}' for f, c in fm)} |")
    L += ["", "## Formatos y botones", "",
          "Formatos: " + ", ".join(f"{f} ×{c}" for f, c in Counter(x["formato"] for x in ads).most_common()),
          "", "Botones: " + ", ".join(f"«{b}» ×{c}" for b, c in Counter(x["boton"] for x in ads if x["boton"]).most_common()),
          "", "## Patrones de texto (pistas automáticas)", ""] + [f"- {p}" for p in patrones(ads)]
    cobrados = LEIDOS[0] or len(crudo)
    L += ["", f"Coste aproximado en Apify: {cobrados * PRECIO:.3f} $ ({cobrados} anuncios × {PRECIO} $)."]
    open(os.path.join(a.salida, "informe.md"), "w").write("\n".join(L) + "\n")
    print(f"Listo: {len(ads)} anuncios de {len(por)} páginas → {a.salida}/informe.md y anuncios.json")
    print(f"Coste aproximado en Apify: {(LEIDOS[0] or len(crudo)) * PRECIO:.3f} $")


if __name__ == "__main__":
    main()
