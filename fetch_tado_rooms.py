#!/usr/bin/env python3
import json
import os
from datetime import datetime, UTC

import requests

TADO_AUTH_URL = "https://auth.tado.com/oauth/token"
TADO_API_BASE = "https://my.tado.com/api/v2"
DEFAULT_CLIENT_ID = "tado-web-app"
DEFAULT_SCOPE = "home.user"


def env(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None or value == "":
        raise SystemExit(f"Missing required environment variable: {name}")
    return value


def get_access_token(username: str, password: str, client_id: str, client_secret: str | None) -> str:
    data = {
        "grant_type": "password",
        "client_id": client_id,
        "scope": DEFAULT_SCOPE,
        "username": username,
        "password": password,
    }
    if client_secret:
        data["client_secret"] = client_secret
    resp = requests.post(TADO_AUTH_URL, data=data, timeout=30)
    resp.raise_for_status()
    return resp.json()["access_token"]


def get_home(home_id: str, token: str) -> dict:
    resp = requests.get(
        f"{TADO_API_BASE}/homes/{home_id}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def get_zones(home_id: str, token: str) -> list[dict]:
    resp = requests.get(
        f"{TADO_API_BASE}/homes/{home_id}/zones",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def get_zone_state(home_id: str, zone_id: int, token: str) -> dict:
    resp = requests.get(
        f"{TADO_API_BASE}/homes/{home_id}/zones/{zone_id}/state",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def build_room(zone: dict, state: dict) -> dict:
    sensor = state.get("sensorDataPoints", {})
    inside = sensor.get("insideTemperature", {})
    humidity = sensor.get("humidity", {})
    overlay = state.get("overlay") or {}
    setting = state.get("setting") or {}
    target_temp = (overlay.get("setting") or setting).get("temperature", {})
    activity = state.get("activityDataPoints") or {}
    heating_power = activity.get("heatingPower") or {}

    return {
        "name": zone["name"],
        "temperature_c": round(float(inside.get("celsius")), 1) if inside.get("celsius") is not None else None,
        "humidity": int(round(float(humidity.get("percentage")))) if humidity.get("percentage") is not None else None,
        "power": "ON" if float(heating_power.get("percentage", 0) or 0) > 0 else "OFF",
        "target": target_temp.get("celsius"),
    }


def summarize(rooms: list[dict]) -> dict:
    rooms_with_temp = [r for r in rooms if r["temperature_c"] is not None]
    coldest = min(rooms_with_temp, key=lambda r: r["temperature_c"]) if rooms_with_temp else None
    warmest = max(rooms_with_temp, key=lambda r: r["temperature_c"]) if rooms_with_temp else None
    avg_temp = round(sum(r["temperature_c"] for r in rooms_with_temp) / len(rooms_with_temp), 1) if rooms_with_temp else None
    return {
        "room_count": len(rooms),
        "average_temperature_c": avg_temp,
        "coldest_room": coldest["name"] if coldest else None,
        "warmest_room": warmest["name"] if warmest else None,
    }


def main() -> None:
    username = env("TADO_USERNAME")
    password = env("TADO_PASSWORD")
    home_id = env("TADO_HOME_ID")
    client_id = env("TADO_CLIENT_ID", DEFAULT_CLIENT_ID)
    client_secret = os.getenv("TADO_CLIENT_SECRET")

    token = get_access_token(username, password, client_id, client_secret)
    home = get_home(home_id, token)
    zones = get_zones(home_id, token)

    rooms = []
    for zone in zones:
        state = get_zone_state(home_id, zone["id"], token)
        rooms.append(build_room(zone, state))

    payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "source": "tado-api",
        "home": {
            "id": int(home_id),
            "name": home.get("name"),
        },
        "summary": summarize(rooms),
        "rooms": rooms,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
