# Herramienta 1 · Espía de la Biblioteca de anuncios

Objetivo: encontrar los anuncios que la competencia del usuario lleva semanas o meses pagando (señal de que le traen
clientes) y explicar por qué funcionan.

## 1 · Entiende el negocio (sin gastar)

```bash
python3 ~/.claude/skills/anuncios/scripts/comun.py https://suweb.es
```

Con el título, la descripción, las cabeceras y el texto, deduce y **enséñale al usuario en 4 líneas** (que lo confirme
o corrija antes de gastar nada):

- Sector y servicio principal (p. ej. «fisioterapia deportiva y pilates terapéutico»).
- Ciudad o zona, y país (código de 2 letras para la biblioteca: ES, MX, AR…).
- 2-4 palabras clave de búsqueda como las escribiría un anunciante del sector («fisioterapia deportiva»,
  «pilates terapéutico»). Mejor 2 palabras que 1 genérica: «fisioterapia» a secas trae mucho ruido.
- 2-5 competidores con nombre (de su web, de una búsqueda en Google «<sector> <ciudad>» o de los que te diga).

## 2 · Busca

```bash
python3 ~/.claude/skills/anuncios/scripts/espia.py \
  --palabra "fisioterapia deportiva" --palabra "pilates terapéutico" \
  --competidor "Nombre de su página" --competidor https://www.facebook.com/supagina \
  --pais ES --max 20 --imagenes --salida ~/Anuncios/espia-<sector>
```

- `--max 20` por búsqueda es suficiente para empezar (cuesta ≈ 0,015 $ cada 20 anuncios). Sube a 50 solo si lo pide.
- Si un competidor sale como «no aparece ninguna página», o no anuncia ahora o su página se llama distinto: pide la
  URL de su Facebook. **Que un competidor no anuncie también es un dato**: díselo.
- Errores: `FALTA_CLAVE` (guía para sacar el token de Apify, README), `SIN_SALDO` (se acabaron los 5 $ gratis del
  mes), `SIN_ANUNCIOS` (prueba otra palabra).

## 3 · Lee el informe y explícalo

Lee `informe.md` y `anuncios.json`. Mira las imágenes de `img/` del top. Entonces:

1. **Descarta el ruido**: la búsqueda por palabra trae universidades, másteres, tiendas o anuncios de otros países.
   Quédate con los que venden lo mismo que el usuario a su mismo cliente.
2. **Top 5 de ganadores** del sector, cada uno con: quién, días activo, formato, el gancho (primera frase literal),
   la oferta, el botón y **por qué crees que funciona** (la palanca: dolor concreto, prueba, método con nombre,
   contacto directo por WhatsApp, oferta de entrada…).
3. **Patrones que se repiten** (3-5), con cuántos anuncios los usan. Ejemplo: «4 de 6 abren con una pregunta del
   paciente».
4. **Huecos**: lo que nadie está diciendo y el usuario podría ocupar.
5. Guarda tu análisis en `~/Anuncios/espia-<sector>/analisis.md` y ofrece el siguiente paso: «¿Te reescribo tus
   anuncios con esto?» (herramienta 2) o «¿Te preparo las imágenes?» (herramienta 3).

Reglas: la señal de ganador es lo que se ve desde fuera (tiempo activo, variantes, repetición). El gasto y los
resultados de otros anunciantes **no son públicos**: nunca digas «este anuncio convierte un X %».
