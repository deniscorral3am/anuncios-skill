# Probado · 8 de noviembre de 2026

Mac (macOS 26), Python 3.9.6 del sistema, sin librerías extra.

## Actor de Apify

| Actor | Resultado | Precio por anuncio |
|---|---|---|
| `curious_coder/facebook-ads-library-scraper` | Funciona. Devuelve texto, titular, botón, formato, fecha de inicio, nº de variantes (`collation_count`) y el total de anuncios activos de la búsqueda | 0,00075 $ |
| `apify/facebook-ads-scraper` | Funciona (lo usa otra skill), pero cuesta casi 8 veces más | 0,0058 $ |

Me quedo con `curious_coder`. Prueba inicial: búsqueda «fisioterapia» en ES, 10 anuncios en unos 40 s.

## 1 · Espía (real)

```bash
python3 scripts/comun.py https://www.tu-clinica.es
# → título «Centro de fisioterapia deportiva y recuperación funcional en Valencia», cabeceras: Pilates Terapéutico,
#   Asesoramiento deportivo… → palabras «fisioterapia deportiva» y «pilates terapéutico»

python3 scripts/espia.py --palabra "fisioterapia deportiva" --palabra "pilates terapéutico" --competidor "Competidor D" \
  --pais ES --max 10 --imagenes --salida ejemplo/espia-<tu-sector>
# «Competidor D»: no aparece ninguna página con ese nombre con anuncios activos en ES
# Listo: 20 anuncios de 14 páginas · coste ≈ 0,015 $ · 52 s
```

- La biblioteca dice que hay 361 anuncios activos para «fisioterapia deportiva» y 48 para «pilates terapéutico» (ES).
- Top real: Competidor B (506 días activo), Competidor A (4 anuncios de 76 a 289 días), Competidor C (110 días), Posturopodia Paco Mateos, Fisio-Innova (botón de WhatsApp).
- Ruido esperado al buscar por palabra: universidades y másteres (UNIR, CEU) y una tienda de material de pilates. La
  guía le dice a Claude que los descarte.
- Las 15 imágenes del top, reducidas a 600 px (1,6 MB en total).
- Competidor por nombre: `--competidor "Competidor A" --max 10` → encuentra la página (ID de su página) y
  saca sus 10 anuncios. Coste ≈ 0,019 $ (15 para encontrar la página + 10).
- `--rehacer` rehace el informe desde `crudo.json` sin gastar nada.

## 2 · Creador

- Sobre 2 anuncios de una clínica inventada (`ejemplo/creador/mis-anuncios.md`) → `ejemplo/creador/reescritos.md`:
  qué fallaba, texto nuevo con la palanca de un ganador real (días activo citados), titular, botón y variante B. Los
  datos que no se conocen quedan entre corchetes, no se inventan.
- `presupuesto.py` con un CSV de **datos ficticios** marcados como tales (`ejemplo/presupuesto/`): clasifica bien
  ESCALAR / MANTENER / APAGAR y calcula el dinero que se libera.
- Cuenta de Meta (`cuenta.py`), sin token real:
  - sin token → `FALTA_CLAVE` con instrucciones; sin cuenta → `FALTA_CUENTA`.
  - token falso contra la API Graph real → Meta responde con el error 190 → `TOKEN_MAL`. La petición y el control de
    errores funcionan.
  - lectura de anuncios y métricas probada con respuestas de la API simuladas (con la forma real de la Marketing
    API): saca texto, titular, botón, presupuesto diario y resultado (conversaciones de WhatsApp), y su `metricas.csv`
    entra bien en `presupuesto.py`.
  - **Sin probar con una cuenta publicitaria real** (hace falta un token con `ads_read`).

## 3 · Creatividades

- Sin claves → `SIN_CLAVE_IMAGEN` y `ejemplo/creatividades/prompts.md` con los 2 prompts listos para pegar.
- Con la `OPENROUTER_API_KEY` de Denis → OpenRouter responde `401 User not found` (la clave ya no vale). El script
  avisa y sigue. **La generación de imágenes no se ha podido probar de verdad**: falta una clave válida de OpenAI,
  Gemini u OpenRouter.

## Otros

- `instalar_comandos.py --destino <carpeta de prueba>` crea `/anuncios-espia`, `/anuncios-creador` y
  `/anuncios-creatividades`. No se ha instalado en `~/.claude/skills`.
- Gasto total de Apify en estas pruebas: unos 0,05 $ (unos 65 anuncios).
