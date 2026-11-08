#!/usr/bin/env python3
"""CREATIVIDADES · convierte los briefs de imagen en imágenes listas para el anuncio (o en prompts si no tienes clave).

Entrada: un JSON con una lista de briefs (lo escribe Claude a partir de los anuncios ganadores):
  [{"id": "A1", "formato": "4:5", "prompt": "Foto realista de…", "texto_en_imagen": "Vuelve a correr sin dolor",
    "inspirado_en": "id del anuncio ganador", "por_que": "…"}]

Proveedor (--proveedor auto elige el primero que tengas en ~/Anuncios/.env o en el entorno):
  OPENAI_API_KEY                     → OpenAI gpt-image-1
  GEMINI_API_KEY o GOOGLE_API_KEY    → Google gemini-2.5-flash-image
  OPENROUTER_API_KEY                 → OpenRouter google/gemini-2.5-flash-image
  ninguno                            → deja prompts.md listo para pegar en ChatGPT, Gemini, Midjourney o Canva

Uso:
  python3 creatividades.py --briefs briefs.json --salida ~/Anuncios/creatividades [--proveedor auto] [--solo A1]
"""
import argparse, base64, json, os, sys, urllib.error, urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comun import CARPETA, cargar_env  # noqa: E402

TAM_OPENAI = {"1:1": "1024x1024", "4:5": "1024x1536", "9:16": "1024x1536", "16:9": "1536x1024", "1.91:1": "1536x1024"}


def prompt_final(b):
    p = b["prompt"].strip()
    if b.get("texto_en_imagen"):
        p += (f' Incluye este texto exacto, en español, grande y legible, con buen contraste: "{b["texto_en_imagen"]}".'
              " Sin más texto que ese, sin faltas de ortografía.")
    p += f" Formato {b.get('formato', '1:1')}, pensado para un anuncio de Instagram y Facebook."
    return p


def post(url, cuerpo, cabeceras):
    req = urllib.request.Request(url, data=json.dumps(cuerpo).encode(),
                                 headers={"Content-Type": "application/json", **cabeceras})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"{e.code}: {e.read().decode(errors='ignore')[:300]}")


def con_openai(b, k):
    d = post("https://api.openai.com/v1/images/generations",
             {"model": "gpt-image-1", "prompt": prompt_final(b), "size": TAM_OPENAI.get(b.get("formato"), "1024x1024"), "n": 1},
             {"Authorization": f"Bearer {k}"})
    return base64.b64decode(d["data"][0]["b64_json"])


def con_gemini(b, k):
    d = post("https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent",
             {"contents": [{"parts": [{"text": prompt_final(b)}]}],
              "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": b.get("formato", "1:1")}}},
             {"x-goog-api-key": k})
    for p in d["candidates"][0]["content"]["parts"]:
        if "inlineData" in p:
            return base64.b64decode(p["inlineData"]["data"])
    raise RuntimeError("Gemini no ha devuelto imagen")


def con_openrouter(b, k):
    d = post("https://openrouter.ai/api/v1/chat/completions",
             {"model": os.environ.get("OPENROUTER_IMAGE_MODEL", "google/gemini-2.5-flash-image"),
              "messages": [{"role": "user", "content": prompt_final(b)}], "modalities": ["image", "text"],
              "image_config": {"aspect_ratio": b.get("formato", "1:1")}},
             {"Authorization": f"Bearer {k}"})
    imgs = d["choices"][0]["message"].get("images") or []
    if not imgs:
        raise RuntimeError("OpenRouter no ha devuelto imagen")
    return base64.b64decode(imgs[0]["image_url"]["url"].split(",", 1)[1])


PROVEEDORES = [("openai", "OPENAI_API_KEY", con_openai), ("gemini", "GEMINI_API_KEY", con_gemini),
               ("gemini", "GOOGLE_API_KEY", con_gemini), ("openrouter", "OPENROUTER_API_KEY", con_openrouter)]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--briefs", required=True)
    ap.add_argument("--salida", default=os.path.join(CARPETA, "creatividades"))
    ap.add_argument("--proveedor", default="auto", choices=["auto", "openai", "gemini", "openrouter", "ninguno"])
    ap.add_argument("--solo", action="append", default=[], help="genera solo estos id (para probar con uno)")
    a = ap.parse_args()
    cargar_env()
    todos = json.load(open(os.path.expanduser(a.briefs)))
    briefs = [b for b in todos if b["id"] in a.solo] if a.solo else todos
    out = os.path.expanduser(a.salida)
    os.makedirs(out, exist_ok=True)

    L = ["# Prompts de imagen", "", "Pégalos tal cual en ChatGPT (imágenes), Gemini, Midjourney o Canva.", ""]
    for b in todos:
        L += [f"## {b['id']} · formato {b.get('formato', '1:1')}" + (f" · inspirado en {b['inspirado_en']}" if b.get("inspirado_en") else ""),
              "", prompt_final(b), ""] + ([f"Por qué: {b['por_que']}", ""] if b.get("por_que") else [])
    open(os.path.join(out, "prompts.md"), "w").write("\n".join(L))

    elegido = None
    if a.proveedor != "ninguno":
        for nombre, var, fn in PROVEEDORES:
            if (a.proveedor in ("auto", nombre)) and os.environ.get(var, "").strip():
                elegido = (nombre, os.environ[var].strip(), fn)
                break
    if not elegido:
        print(f"SIN_CLAVE_IMAGEN: he dejado los {len(todos)} prompts en {out}/prompts.md. "
              "Si quieres que genere las imágenes, pon OPENAI_API_KEY, GEMINI_API_KEY u OPENROUTER_API_KEY en ~/Anuncios/.env.")
        return
    nombre, k, fn = elegido
    print(f"Generando {len(briefs)} imágenes con {nombre}…")
    ok = 0
    for b in briefs:
        try:
            datos = fn(b, k)
            ruta = os.path.join(out, f"{b['id']}.png")
            open(ruta, "wb").write(datos)
            ok += 1
            print(f"  {b['id']} → {ruta}")
        except Exception as e:
            print(f"  {b['id']} falló: {e}")
    print(f"Listo: {ok}/{len(briefs)} imágenes en {out} (y los prompts en prompts.md)")


if __name__ == "__main__":
    main()
