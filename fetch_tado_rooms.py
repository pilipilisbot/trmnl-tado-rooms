#!/usr/bin/env python3
import json
import subprocess
from datetime import datetime, UTC

raw = subprocess.check_output([
    'python3', '/home/openclaw/.local/bin/pilipilis_tado.py', 'rooms'
], text=True)
rooms = []
for line in raw.strip().splitlines():
    parts = line.split('|')
    item = {'name': parts[0]}
    for part in parts[1:]:
        k, v = part.split('=', 1)
        item[k] = v
    rooms.append({
        'name': item['name'],
        'temperature_c': round(float(item['inside']), 1),
        'humidity': int(item['humidity']),
        'power': item['power'],
        'target': None if item['target'] == 'None' else item['target'],
    })

coldest = min(rooms, key=lambda r: r['temperature_c']) if rooms else None
warmest = max(rooms, key=lambda r: r['temperature_c']) if rooms else None
avg_temp = round(sum(r['temperature_c'] for r in rooms) / len(rooms), 1) if rooms else None

payload = {
    'generated_at': datetime.now(UTC).isoformat(),
    'source': 'tado',
    'summary': {
        'room_count': len(rooms),
        'average_temperature_c': avg_temp,
        'coldest_room': coldest['name'] if coldest else None,
        'warmest_room': warmest['name'] if warmest else None,
    },
    'rooms': rooms,
}
print(json.dumps(payload, ensure_ascii=False, indent=2))
