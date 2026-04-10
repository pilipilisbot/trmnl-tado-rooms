# trmnl-tado-rooms

Plugin privat per **TRMNL** que mostra les temperatures i humitat de les habitacions de **Tado**.

Repo: https://github.com/pilipilisbot/trmnl-tado-rooms

## Què canvia ara

Aquest repo ja **no depèn** del script local `pilipilis_tado.py`.
Ara parla **directament amb l'API de Tado**.

## Què inclou

- `fetch_tado_rooms.py`: client standalone que consulta l'API de Tado i genera JSON
- `rooms_sample.json`: exemple del payload que consumirà TRMNL
- `example_template.liquid`: template base perquè el plugin es vegi bé a TRMNL

## Variables d'entorn necessàries

```bash
export TADO_USERNAME="tu-email-tado"
export TADO_PASSWORD="la-teva-password-tado"
export TADO_HOME_ID="123456"
```

### Opcional

```bash
export TADO_CLIENT_ID="tado-web-app"
export TADO_CLIENT_SECRET=""
```

En la majoria de casos, amb `TADO_USERNAME`, `TADO_PASSWORD` i `TADO_HOME_ID` n'hi ha prou.

## Instal·lació local

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install requests
python3 fetch_tado_rooms.py > rooms.json
```

## Exemple de payload

```json
{
  "generated_at": "2026-04-10T15:00:00Z",
  "source": "tado-api",
  "home": {
    "id": 123456,
    "name": "Casa"
  },
  "summary": {
    "room_count": 6,
    "average_temperature_c": 18.9,
    "coldest_room": "Estudi",
    "warmest_room": "Habitació papes"
  },
  "rooms": [
    {
      "name": "Menjador",
      "temperature_c": 19.6,
      "humidity": 65,
      "power": "OFF",
      "target": null
    }
  ]
}
```

## Com fer-lo servir a TRMNL

L'estratègia recomanada és **Private Plugin + Polling**.

### Pas 1. Publica el JSON en una URL pública

TRMNL necessita llegir una URL HTTP/HTTPS.

Opcions:
- endpoint teu
- Cloudflare Worker
- Vercel
- GitHub Action + GitHub Pages
- qualsevol hosting estàtic o petit backend

### Pas 2. Crea el plugin a TRMNL

A TRMNL:

1. ves a **Plugins**
2. crea un **Private Plugin**
3. tria **Polling** com a strategy
4. posa la URL pública del `rooms.json`
5. desa el plugin
6. ves a **Edit Markup**
7. enganxa el contingut de `example_template.liquid`

### Pas 3. Usa aquestes variables al template

- `summary.average_temperature_c`
- `summary.room_count`
- `summary.coldest_room`
- `summary.warmest_room`
- `rooms`
- `rooms[0].name`
- `rooms[0].temperature_c`
- `rooms[0].humidity`

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

Perquè sigui útil cada dia, el normal és executar `fetch_tado_rooms.py` periòdicament i publicar el JSON.

Per exemple cada 5 o 10 minuts.

## Notes

- Aquest repo no necessita el wrapper local de Pilipilis.
- Ara és un client standalone contra Tado.
- El següent pas natural, si vols fer-lo realment desplegable, és afegir-li:
  - `requirements.txt`
  - `.env.example`
  - GitHub Action o petit deploy per publicar `rooms.json`
