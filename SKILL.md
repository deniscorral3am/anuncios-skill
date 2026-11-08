---
name: anuncios
description: Tres herramientas para anuncios de Meta (Facebook e Instagram). 1) Espía - pegas tu web, deduce tu sector y tu competencia y saca de la Biblioteca de anuncios de Meta cada anuncio activo ordenado por señal de ganador (días activo, variantes, mensajes repetidos). 2) Creador - reescribe tus anuncios (pegados o leídos de tu cuenta publicitaria en solo lectura) con lo que ya funciona en tu sector y te dice dónde mover el presupuesto según tus métricas. 3) Creatividades - briefs y prompts de imagen inspirados en los ganadores y, si tienes clave de OpenAI o Gemini, las imágenes. Úsala cuando digan /anuncios, «comenta ANUNCIOS», «espía los anuncios de mi competencia», «qué anuncios funcionan en mi sector», «biblioteca de anuncios», «reescribe mis anuncios», «mejora mis anuncios de Meta», «dónde muevo el presupuesto», «hazme las imágenes del anuncio» o peguen su web hablando de anuncios.
---

# /anuncios · espía, creador y creatividades

Todo se guarda en `~/Anuncios/` (claves en `~/Anuncios/.env`, nunca en el chat ni en esta carpeta). Scripts en
`~/.claude/skills/anuncios/scripts/` (Python 3, solo librería estándar).

| # | Herramienta | Guía | Script | Necesita |
|---|---|---|---|---|
| 1 | Espía de la biblioteca | `herramientas/espia.md` | `espia.py` (+ `comun.py` para leer su web) | `APIFY_TOKEN` |
| 2 | Creador de anuncios | `herramientas/creador.md` | `cuenta.py`, `presupuesto.py` | nada (o `META_ACCESS_TOKEN` para leer su cuenta) |
| 3 | Creatividades | `herramientas/creatividades.md` | `creatividades.py` | nada (o `OPENAI_API_KEY` / `GEMINI_API_KEY`) |

## Cómo arrancar

1. Si escribe solo `/anuncios` o pega su web: lanza **1 → 2 → 3** en orden, parando tras cada una para que vea el
   resultado. Si pide una sola cosa («reescribe este anuncio», «hazme las imágenes»), ve directo a esa guía.
2. Primera vez: comprueba si hay `APIFY_TOKEN` (`python3 -c "import sys; sys.path.insert(0,'$HOME/.claude/skills/anuncios/scripts'); import comun; comun.cargar_env(); import os; print(bool(os.environ.get('APIFY_TOKEN')))"`).
   Si no hay, explica en 3 pasos cómo sacarlo (cuenta gratis en apify.com → Settings → API & Integrations → copiar
   token → crear `~/Anuncios/.env` con `APIFY_TOKEN=...`) y espera. Nunca le pidas que pegue la clave en el chat.
3. Lee la guía de la herramienta y síguela.

## Reglas

- **Gasta poco**: 20 anuncios por búsqueda de entrada (≈ 0,015 $). Di siempre lo que ha costado (lo imprime el script).
- **No inventes cifras**: ni del usuario (precios, años, clientes) ni de la competencia (gasto o conversiones de otros
  no son públicos). La señal de ganador es tiempo activo + variantes + repetición, y así se explica.
- **Solo lectura** en la cuenta de Meta: esta skill no crea, no pausa, no cambia presupuestos ni publica. Propone; el
  usuario decide y lo hace él.
- Copia la palanca y la estructura de los ganadores, **nunca su texto literal**, su marca ni sus imágenes.
- Español de España, tú, frases cortas, sin emojis en tus explicaciones (en el anuncio, solo si el sector los usa).
- Opcional: `python3 scripts/instalar_comandos.py` crea `/anuncios-espia`, `/anuncios-creador` y
  `/anuncios-creatividades` como comandos sueltos.

Al acabar, resume en 5 líneas: qué ha encontrado, qué ha reescrito, qué imágenes o prompts ha dejado, dónde están los
archivos y cuánto ha costado.
