from flask import Flask, render_template
import requests, os

app = Flask(__name__)

# Pokemones básicos (sin pre‑evolución)
BASIC_POKEMON = ["pichu", "charmander", "squirtle", "bulbasaur"]

# Colores por tipo
TYPE_COLORS = {
    'normal':'#A8A77A','fire':'#EE8130','water':'#6390F0','electric':'#F7D02C',
    'grass':'#7AC74C','ice':'#96D9D6','fighting':'#C22E28','poison':'#A33EA1',
    'ground':'#E2BF65','flying':'#A98FF3','psychic':'#F95587','bug':'#A6B91A',
    'rock':'#B6A136','ghost':'#735797','dragon':'#6F35FC','dark':'#705746',
    'steel':'#B7B7CE','fairy':'#D685AD'
}

# Temas de fondo por tipo
THEMES = {
    'fire':     {'bg':'#a80b0b','text':'#ffffff','accent':'#5d0a0a','chip':'#d96b4f'},
    'water':    {'bg':'#0b4ea2','text':'#ffffff','accent':'#08376f','chip':'#5fa9ff'},
    'electric': {'bg':'#f1d100','text':'#111111','accent':'#9c8f00','chip':'#ffe45f'},
    'grass':    {'bg':'#1f7a1f','text':'#111111','accent':'#155515','chip':'#8ed081'},
    'default':  {'bg':'#222','text':'#ffffff','accent':'#111','chip':'#cccccc'}
}

def text_color_for(hex_color: str) -> str:
    if not hex_color or not hex_color.startswith('#') or len(hex_color) != 7:
        return '#111'
    r = int(hex_color[1:3], 16) / 255.0
    g = int(hex_color[3:5], 16) / 255.0
    b = int(hex_color[5:7], 16) / 255.0
    lum = 0.2126*r + 0.7152*g + 0.0722*b
    return '#111' if lum > 0.6 else '#fff'

def get_ability_effect(url: str) -> str:
    r = requests.get(url, timeout=20)
    if r.status_code != 200:
        return ''
    data = r.json()
    for e in data.get('effect_entries', []):
        if e['language']['name'] == 'en':
            return e['effect']
    return ''

def get_pokemon_data(name: str):
    r = requests.get(f"https://pokeapi.co/api/v2/pokemon/{name.lower()}", timeout=20)
    if r.status_code != 200:
        return None
    d = r.json()

    sprite_anim = (
        d.get('sprites', {})
         .get('versions', {})
         .get('generation-v', {})
         .get('black-white', {})
         .get('animated', {})
         .get('front_default')
    )
    sprite_static = d.get('sprites', {}).get('front_default')
    artwork = (
        d.get('sprites', {})
         .get('other', {})
         .get('official-artwork', {})
         .get('front_default')
    )

    abilities = [{'name': a['ability']['name'],
                  'effect': get_ability_effect(a['ability']['url'])}
                 for a in d.get('abilities', [])]

    p = {
        'name': d['name'],
        'types': [t['type']['name'] for t in d.get('types', [])],
        'hp': d['stats'][0]['base_stat'],
        'attack': d['stats'][1]['base_stat'],
        'defense': d['stats'][2]['base_stat'],
        'base_experience': d['base_experience'],
        'abilities': abilities,
        'sprite': sprite_anim or sprite_static,
        'sprite_static': sprite_static,
        'artwork': artwork
    }
    return p

def get_evolutions(name: str):
    r = requests.get(f"https://pokeapi.co/api/v2/pokemon-species/{name.lower()}", timeout=20)
    if r.status_code != 200:
        return []
    species = r.json()
    chain_url = species.get('evolution_chain', {}).get('url')
    if not chain_url:
        return []
    chain = requests.get(chain_url, timeout=20).json().get('chain', {})
    out, node = [], chain
    while node:
        out.append(node['species']['name'])
        node = node['evolves_to'][0] if node.get('evolves_to') else None
    return out[1:] if len(out) > 1 else []

def get_sprite_thumb(name: str) -> str:
    r = requests.get(f"https://pokeapi.co/api/v2/pokemon/{name.lower()}", timeout=20)
    if r.status_code != 200:
        return ""
    d = r.json()
    anim = (d.get('sprites', {}).get('versions', {}).get('generation-v', {})
            .get('black-white', {}).get('animated', {}).get('front_default'))
    static_ = d.get('sprites', {}).get('front_default')
    return anim or static_

def get_double_damage(types):
    dmg_from, dmg_to = [], []
    for t in types:
        r = requests.get(f"https://pokeapi.co/api/v2/type/{t}", timeout=20)
        if r.status_code != 200:
            continue
        td = r.json()
        dmg_from += [x['name'] for x in td['damage_relations']['double_damage_from']]
        dmg_to   += [x['name'] for x in td['damage_relations']['double_damage_to']]
    return sorted(set(dmg_from)), sorted(set(dmg_to))

def build_damage_pills(names):
    pills = []
    for n in names:
        bg = TYPE_COLORS.get(n.lower(), '#cccccc')
        fg = text_color_for(bg)
        pills.append({'name': n.capitalize(), 'bg': bg, 'fg': fg})
    return pills

def pick_theme(types):
    t = types[0] if types else 'default'
    return THEMES.get(t, THEMES['default'])


@app.route("/")
def index():
    
    pokemons = []
    for n in BASIC_POKEMON:
        thumb = get_sprite_thumb(n)  
        pokemons.append({"name": n.capitalize(), "slug": n, "sprite": thumb})
    return render_template(
        "index.html",
        pokemon_list=BASIC_POKEMON,  
        themes=THEMES,
        pokemons=pokemons           
    )

@app.route("/pokemon/<name>")
def pokemon(name):
    if name.lower() not in BASIC_POKEMON:
        return "<h2 style='text-align:center;margin-top:3rem'>Pokémon not available!</h2>"
    p = get_pokemon_data(name)
    if not p:
        return "<h2 style='text-align:center;margin-top:3rem'>Pokémon not found!</h2>"

    evol_names = get_evolutions(name)
    evols = [{'name': n.capitalize(), 'sprite': get_sprite_thumb(n)} for n in evol_names]

    dmg_from, dmg_to = get_double_damage(p['types'])
    pills_from = build_damage_pills(dmg_from)
    pills_to = build_damage_pills(dmg_to)

    theme = pick_theme(p['types'])
    type_badge = build_damage_pills([p['types'][0]])[0] if p['types'] else {'bg': '#ccc', 'fg': '#111', 'name': 'Unknown'}

    #Render normal (para la web)
    html = render_template(
        "pokemon.html",
        p=p, evols=evols,
        pills_from=pills_from, pills_to=pills_to,
        theme=theme, type_badge=type_badge,
        export=False,  # modo normal
        inline_css="", inline_js=""
    )

    #Render para exportar (CSS/JS incrustados)
    try:
        css_path = os.path.join(app.static_folder, "css", "style.css")
        js_path  = os.path.join(app.static_folder, "js", "main.js")
        inline_css = open(css_path, "r", encoding="utf-8").read() if os.path.exists(css_path) else ""
        inline_js  = open(js_path, "r", encoding="utf-8").read()  if os.path.exists(js_path)  else ""

        export_html = render_template(
            "pokemon.html",
            p=p, evols=evols,
            pills_from=pills_from, pills_to=pills_to,
            theme=theme, type_badge=type_badge,
            export=True,              # activa inline
            inline_css=inline_css,    # CSS incrustado
            inline_js=inline_js       # JS incrustado
        )

        os.makedirs("exports", exist_ok=True)
        fname = f"{p['name'].capitalize()}.html"
        with open(os.path.join("exports", fname), "w", encoding="utf-8") as f:
            f.write(export_html)
        # Nota: el archivo queda en /exports/<Nombre>.html
    except Exception as e:
        # Si algo falla al exportar, no rompemos la vista web
        print("Export error:", e)

    return html

if __name__ == "__main__":
    app.run(debug=True)
