# trmnl-tado-rooms

Plugin privat per **TRMNL** que mostra les temperatures i humitat de les habitacions de **Tado**.

Repo: https://github.com/pilipilisbot/trmnl-tado-rooms

## Què inclou

- `fetch_tado_rooms.py`: script que extreu l'estat actual de Tado i genera JSON
- `rooms_sample.json`: exemple real del payload que consumirà TRMNL
- `example_template.liquid`: template base perquè el plugin es vegi bé a TRMNL

## Com funciona

L'estratègia recomanada per a TRMNL és:

1. generar o servir un JSON HTTP amb les dades de Tado
2. crear un **Private Plugin** a TRMNL amb estratègia **Polling**
3. enganxar el template Liquid del repo

Això és més simple i mantenible que intentar incrustar la lògica de Tado dins del plugin.

## 1. Generar el JSON

Executa:

```bash
python3 fetch_tado_rooms.py > rooms.json
```

## 2. Publicar el JSON perquè TRMNL el pugui llegir

TRMNL amb **Polling** necessita una URL accessible per HTTP/HTTPS.

Opcions fàcils:
- GitHub Pages o qualsevol hosting estàtic, si publiques un `rooms.json`
- petit endpoint propi
- Cloudflare Worker / Vercel / PythonAnywhere / GitHub Action que regeneri el fitxer

Exemple d'URL final:

```text
https://example.com/tado/rooms.json
```

## 3. Crear el plugin a TRMNL

A TRMNL:

1. Ves a **Plugins**
2. Crea un **Private Plugin**
3. Tria estratègia **Polling**
4. A **Polling URL(s)** posa la URL del teu `rooms.json`
5. Desa el plugin
6. Ves a **Edit Markup**
7. Enganxa el contingut de `example_template.liquid`

## 4. Variables que farà servir el template

Com que el Polling retorna JSON, podràs usar directament:

- `summary.average_temperature_c`
- `summary.room_count`
- `summary.coldest_room`
- `summary.warmest_room`
- `rooms`
- `rooms[0].name`
- `rooms[0].temperature_c`

## Template base

```liquid
<div class="layout layout--col gap--space-between">
  <div>
    <div class="text--xxsmall text--subtle">Tado · Habitacions</div>
    <div class="text--small">Mitjana {{ summary.average_temperature_c }}°C · {{ summary.room_count }} estances</div>
  </div>

  <div class="grid grid--cols-2 gap--small">
    {% for room in rooms limit:6 %}
    <div class="item">
      <div class="text--xsmall text--subtle">{{ room.name }}</div>
      <div class="text--large">{{ room.temperature_c }}°</div>
      <div class="text--xxsmall">Hum {{ room.humidity }}%{% if room.power == 'ON' %} · 🔥{% endif %}</div>
    </div>
    {% endfor %}
  </div>

  <div class="text--xxsmall text--subtle">
    Freda: {{ summary.coldest_room }} · Calenta: {{ summary.warmest_room }}
  </div>
</div>
```

## Publicació automàtica recomanada

Si vols que sigui usable de veritat, el següent pas és muntar una automatització que:

- executi `fetch_tado_rooms.py`
- publiqui `rooms.json` a una URL pública
- refresqui periòdicament

Per exemple cada 5 o 10 minuts.

## Notes

- Aquest repo no publica secrets.
- El script depèn del wrapper local `pilipilis_tado.py` del host on s'executa.
- Si vols fer-ho portable, el següent pas és desacoblar-lo i parlar directament amb l'API de Tado o amb un endpoint teu intermedi.
