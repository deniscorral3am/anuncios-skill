# Herramienta 3 · Creatividades (imágenes)

Objetivo: imágenes para los anuncios nuevos inspiradas en lo que ya funciona, o los prompts listos si no tiene clave.

## 1 · Mira lo que funciona

Abre las imágenes del top en `~/Anuncios/espia-*/img/` y apunta qué tienen en común: foto real o diseño, persona o
producto, texto en la imagen (cuánto y dónde), colores, plano. Eso manda más que tu gusto.

## 2 · Escribe los briefs

Un brief por anuncio reescrito, en `~/Anuncios/briefs.json`:

```json
[{"id": "A1", "formato": "4:5", "prompt": "Fotografía realista de…", "texto_en_imagen": "Vuelve a entrenar sin miedo",
  "inspirado_en": "Competidor X (289 días activo)", "por_que": "…"}]
```

- `formato`: 4:5 o 1:1 para el feed, 9:16 para historias y reels.
- `prompt`: escena concreta (quién, qué hace, dónde, luz, plano), aspecto de foto real hecha con móvil, sin estética de
  banco de imágenes. Personas que se parezcan a su cliente real.
- `texto_en_imagen`: 3-7 palabras como mucho, el gancho del anuncio. Opcional.
- Nunca pidas logotipos o marcas de otros, ni caras de personas reales.

## 3 · Genera

```bash
python3 ~/.claude/skills/anuncios/scripts/creatividades.py --briefs ~/Anuncios/briefs.json --salida ~/Anuncios/creatividades
```

- Usa la primera clave que encuentre: `OPENAI_API_KEY` (gpt-image-1), `GEMINI_API_KEY`/`GOOGLE_API_KEY`
  (gemini-2.5-flash-image) u `OPENROUTER_API_KEY`. Avísale antes de que cada imagen cuesta unos céntimos en su cuenta.
  Prueba primero con una (`--solo A1`), enséñasela y sigue si le gusta.
- Sin clave: deja `prompts.md` para pegar en ChatGPT, Gemini o Canva. No es un error: díselo así.

## 4 · Revisa

Abre cada imagen. Si el texto sale con faltas o deformado, regenera o propón poner el texto encima en Canva. Comprueba
que no tapa nada importante y que se lee en el móvil.
