# Anuncios · espía, creador y creatividades para Meta

Escribes `/anuncios` en Claude Code, pegas tu web y te investiga tu sector: encuentra los anuncios que tu competencia
lleva meses pagando en la Biblioteca de anuncios de Meta, te explica por qué funcionan, reescribe los tuyos con lo que
ya funciona, te dice dónde mover el presupuesto y te prepara las imágenes.

| # | Herramienta | Qué hace |
|---|---|---|
| 1 | **Espía** | Deduce tu sector y tus competidores desde tu web, saca sus anuncios activos de la Biblioteca de anuncios de Meta (Facebook e Instagram) y los ordena por señal de ganador: días activo, número de variantes y textos repetidos. Informe con formatos, textos, titulares y botones. |
| 2 | **Creador** | Reescribe tus anuncios (los pegas o los lee de tu cuenta publicitaria en solo lectura) con los patrones de los ganadores. Con tus métricas, te dice qué escalar, qué apagar y cuánto dinero liberas. |
| 3 | **Creatividades** | Briefs y prompts de imagen inspirados en las creatividades que aguantan. Si tienes clave de OpenAI o Gemini, genera las imágenes; si no, te deja los prompts para ChatGPT, Gemini o Canva. |

Hecha por Denis Corral · [Sell Your AI](https://sellyourai.io)

## Instalación

```bash
git clone https://github.com/deniscorral3am/anuncios-skill ~/.claude/skills/anuncios
```

Abre Claude Code y escribe `/anuncios`. Pega tu web cuando te la pida.

¿Prefieres tres comandos separados? `python3 ~/.claude/skills/anuncios/scripts/instalar_comandos.py` crea
`/anuncios-espia`, `/anuncios-creador` y `/anuncios-creatividades`.

## Qué necesitas

- [Claude Code](https://claude.com/claude-code) y Python 3 (viene con el Mac; no hay que instalar librerías).
- Una cuenta gratis de [Apify](https://apify.com) para leer la Biblioteca de anuncios. Trae 5 $ de saldo al mes y cada
  anuncio cuesta unos 0,00075 $: 20 anuncios ≈ 0,015 $.

Tus claves van en `~/Anuncios/.env` (solo en tu ordenador; nunca las pegues en el chat):

```bash
mkdir -p ~/Anuncios && nano ~/Anuncios/.env
```

```
APIFY_TOKEN=apify_api_...          # obligatorio (console.apify.com → Settings → API & Integrations)
META_ACCESS_TOKEN=...              # opcional: leer tus anuncios y métricas (solo lectura)
META_AD_ACCOUNT_ID=act_...         # opcional
OPENAI_API_KEY=...                 # opcional: generar imágenes (o GEMINI_API_KEY / OPENROUTER_API_KEY)
```

### Conectar tu cuenta publicitaria (opcional)

Sin esto, el creador funciona igual con los anuncios que le pegues.

1. Entra en [developers.facebook.com](https://developers.facebook.com) → Mis apps → Crear app (tipo «Empresa»).
2. Abre el [Explorador de la API Graph](https://developers.facebook.com/tools/explorer), elige tu app, añade el permiso
   `ads_read` y pulsa «Generate Access Token».
3. Pega el token en `~/Anuncios/.env` como `META_ACCESS_TOKEN=...`. Ese token dura unas horas; para uno de larga
   duración, usa un usuario del sistema en el Business Manager con acceso a tu cuenta publicitaria.
4. Compruébalo: `python3 ~/.claude/skills/anuncios/scripts/cuenta.py --comprobar`.

La skill solo lee. No crea, no pausa y no cambia presupuestos: te propone los cambios y los haces tú.

## Ejemplos

- «/anuncios https://miclinica.es» → las tres herramientas en orden.
- «Espía los anuncios de fisioterapia deportiva en España y dime qué tienen en común los que más aguantan.»
- «Reescribe estos dos anuncios con lo que funciona en mi sector: …»
- «Lee mi cuenta publicitaria de los últimos 30 días y dime dónde muevo el presupuesto.»
- «Hazme las imágenes para los anuncios nuevos en 4:5.»

Mira un ejemplo real en [`ejemplo/`](ejemplo/): espionaje del sector de fisioterapia deportiva y pilates terapéutico
(20 anuncios activos), dos anuncios reescritos y los prompts de imagen.

## Lo que hace y lo que no

- La «señal de ganador» es lo que se ve desde fuera: cuánto tiempo lleva un anuncio activo, cuántas variantes tiene y
  si el anunciante repite el mismo texto. Nadie paga meses un anuncio que no le trae clientes. El gasto y los resultados
  de otros anunciantes no son públicos y la skill no se los inventa.
- Copia la palanca y la estructura, nunca el texto ni la marca de otros.
- Archivos que crea: `~/Anuncios/espia-*/` (informe, anuncios, imágenes), `mis-anuncios.md`, `reescritos.md`,
  `briefs.json`, `creatividades/`, `mi-cuenta/`.

## Licencia

MIT. Úsala, cámbiala y compártela.
