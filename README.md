# Intern_Candidates_exercises
Aplicación sencilla en Flask que consume la PokéAPI para:
- Pantalla de **selección** con 4 Pokémon en una línea (sprite pixelado + nombre).
- **Ficha** de cada Pokémon con sprite/artwork, tipo, habilidades (con descripción), evoluciones y “double damage”.
- **Export** de la ficha a `exports/<Nombre>.html` con CSS/JS incrustados.

## Requisitos

- Python 3.9+
- Dependencias:
   -Flask
   -requests
## Ejecución

# (opcional) entorno virtual en Windows PowerShell
python -m venv venv
Set-ExecutionPolicy -Scope Process Bypass
.\venv\Scripts\Activate.ps1

pip install -r requirements.txt
python app.py
abrir http://127.0.0.1:5000
Los mensajes “Debug mode / Running on …” son del servidor de desarrollo de Flask.

# Estructura:
```bash
app.py
templates/
  ├─ index.html     # selector con sprites y nombre por tipo
  └─ pokemon.html   # ficha de detalle
static/
  ├─ css/style.css
  └─ js/main.js
exports/            # se llena al visitar una ficha
```
Cómo funciona

Selector (/)
index.html recibe pokemon_list (p. ej. ["pichu","charmander","squirtle","bulbasaur"]).
Un pequeño script en la página llama a la PokéAPI para:

tomar el sprite (GIF Gen V si existe; si no, front_default; si no, official-artwork);

colorear la “pill” del nombre según el tipo principal.

Ficha (/pokemon/<name>)
app.py consulta PokéAPI para stats, tipos y habilidades (y lee el texto de cada habilidad).
También resuelve evoluciones y double damage por tipo.
Al renderizar, se guarda una versión exportable en exports/.

Personalización rápida

Pokémon del selector: edita BASIC_POKEMON en app.py.

Colores por tipo / tema: TYPE_COLORS y THEMES en app.py.

Tamaños del selector: al final de style.css (clases .poke-grid, .poke-thumb-wrap, .poke-thumb).

Botón “Back”: fijo arriba-izquierda, editable en .back (en style.css).

Notas

Para evitar falsos errores en VS Code con Jinja/CSS inline:

{
  "files.associations": {
    "**/templates/**/*.html": "jinja-html",
    "*.html": "jinja-html"
  },
  "css.validate": false
}
