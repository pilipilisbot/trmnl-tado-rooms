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
        'temperature_c': float(item['inside']),
        'humidity': int(item['humidity']),
        'power': item['power'],
        'target': None if item['target'] == 'None' else item['target'],
    })
print(json.dumps({
    'generated_at': datetime.now(UTC).isoformat(),
    'source': 'tado',
    'rooms': rooms,
}, ensure_ascii=False, indent=2))
