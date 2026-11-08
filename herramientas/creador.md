# Herramienta 2 · Creador de anuncios

Objetivo: reescribir los anuncios del usuario con lo que ya funciona en su sector y decirle dónde mover el presupuesto.

## 1 · Consigue sus anuncios (una de dos)

**A. Los pega.** Texto, titular, botón y qué imagen o vídeo llevan. Guárdalos en `~/Anuncios/mis-anuncios.md`.

**B. Conecta su cuenta publicitaria (solo lectura).** Necesita `META_ACCESS_TOKEN` con permiso `ads_read` en
`~/Anuncios/.env` (README, «Conectar tu cuenta publicitaria»). Nunca le pidas que pegue el token en el chat: que lo
escriba él en el archivo.

```bash
python3 ~/.claude/skills/anuncios/scripts/cuenta.py --comprobar                 # ¿funciona el token? ¿qué cuentas ve?
python3 ~/.claude/skills/anuncios/scripts/cuenta.py --cuenta act_123 --dias 30  # anuncios + métricas
```

Deja `~/Anuncios/mi-cuenta/mis-anuncios.json` y `metricas.csv`. El script solo hace GET: **no cambia nada** en su cuenta.
Errores: `TOKEN_MAL` (caducado), `SIN_PERMISO` (falta ads_read o acceso a esa cuenta), `LIMITE` (espera unos minutos).

Si no quiere conectar nada pero tiene métricas, vale con exportar un CSV del Administrador de anuncios (columnas
nombre del anuncio, importe gastado, resultados, impresiones, clics en el enlace).

## 2 · Necesitas el espionaje

Si no hay `~/Anuncios/espia-*/informe.md` reciente, lanza antes la herramienta 1 (con su web).

## 3 · Reescribe

Por cada anuncio suyo, en `~/Anuncios/reescritos.md`:

1. **Qué falla** en una o dos líneas, comparado con los ganadores (habla de la empresa y no del cliente, lista de
   servicios en vez de un problema, oferta sin concretar, botón que no lleva a ningún sitio…).
2. **Texto nuevo** con la palanca de un ganador concreto (di cuál y cuántos días lleva activo). Se copia la
   estructura y la palanca, **nunca el texto literal** ni el nombre de otro.
3. Titular (≤ 40 caracteres), botón y una **variante B del gancho** para probar.
4. Si el anuncio mezcla varios problemas, propón dividirlo en un anuncio por problema.

Reglas de veracidad: no inventes precios, descuentos, años, número de clientes, reseñas ni resultados. Si hace falta
un dato, deja un hueco entre corchetes (`[precio real de la primera sesión]`) y pregúntaselo. Nada de promesas de
salud o dinero que Meta rechace («cura», «garantizado», «gana X € al mes»). Español de España, tú.

## 4 · Presupuesto

Si hay métricas (`metricas.csv` de `cuenta.py` o un CSV exportado):

```bash
python3 ~/.claude/skills/anuncios/scripts/presupuesto.py --metricas ~/Anuncios/mi-cuenta/metricas.csv [--objetivo 15]
```

Pregunta antes cuál es su coste por resultado aceptable (`--objetivo`); si no lo sabe, usa su media. Explica la tabla
en lenguaje normal: qué escalar (+20 %, no más de golpe), qué apagar y cuánto dinero libera para probar los anuncios
nuevos. Sin métricas, recomienda un arranque sencillo (un conjunto con los textos nuevos y revisar a los 7 días).

Los cambios los hace **él** en el Administrador de anuncios. Esta skill no publica, no pausa y no toca presupuestos.
