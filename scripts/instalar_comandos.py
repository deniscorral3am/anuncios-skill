#!/usr/bin/env python3
"""Crea los tres comandos sueltos (/anuncios-espia, /anuncios-creador, /anuncios-creatividades) como skills pequeñas
que apuntan a esta. Opcional: /anuncios ya hace las tres cosas.

Uso: python3 instalar_comandos.py [--destino ~/.claude/skills]
"""
import argparse, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMANDOS = {
    "anuncios-espia": ("Espía los anuncios activos de tu sector y tu competencia en la Biblioteca de anuncios de Meta y "
                       "los ordena por señal de ganador. Úsala con /anuncios-espia, «espía a mi competencia», «qué anuncia "
                       "mi sector» o cuando peguen su web para ver los anuncios de la competencia.", "espia.md"),
    "anuncios-creador": ("Reescribe tus anuncios de Meta (pegados o leídos de tu cuenta publicitaria) con los patrones de los "
                         "anuncios ganadores de tu sector y te dice dónde mover el presupuesto. Úsala con /anuncios-creador, "
                         "«reescribe mis anuncios», «mejora este anuncio» o «dónde muevo el presupuesto».", "creador.md"),
    "anuncios-creatividades": ("Convierte los anuncios ganadores en briefs y prompts de imagen y, si tienes clave de OpenAI o "
                               "Gemini, genera las imágenes. Úsala con /anuncios-creatividades, «hazme las imágenes del "
                               "anuncio» o «creatividades para Meta».", "creatividades.md"),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--destino", default="~/.claude/skills")
    a = ap.parse_args()
    dest = os.path.expanduser(a.destino)
    for nombre, (desc, guia) in COMANDOS.items():
        d = os.path.join(dest, nombre)
        os.makedirs(d, exist_ok=True)
        ruta = os.path.join(d, "SKILL.md")
        open(ruta, "w").write(
            f"---\nname: {nombre}\ndescription: {desc}\n---\n\n"
            f"Lee y sigue `{os.path.join(BASE, 'herramientas', guia)}` (y las reglas de `{os.path.join(BASE, 'SKILL.md')}`).\n"
            f"Los scripts están en `{os.path.join(BASE, 'scripts')}`.\n")
        print(f"/{nombre} → {ruta}")


if __name__ == "__main__":
    main()
