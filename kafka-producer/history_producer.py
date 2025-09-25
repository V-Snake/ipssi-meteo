import os
import sys
import json
import time
import datetime as dt
from typing import Optional, Dict, Any, List
import requests
from kafka import KafkaProducer


KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
TOPIC = os.getenv("TOPIC", "weather_history_raw")

# Inputs
CITY = os.getenv("CITY", "Paris")
COUNTRY = os.getenv("COUNTRY", "France")
START_DATE = os.getenv("START_DATE")  # YYYY-MM-DD
END_DATE = os.getenv("END_DATE")      # YYYY-MM-DD


def iso_date(d: dt.date) -> str:
    return d.strftime("%Y-%m-%d")


def compute_default_range() -> (str, str):
    today = dt.date.today()
    ten_years_ago = today - dt.timedelta(days=365 * 10)
    return iso_date(ten_years_ago), iso_date(today)


def get_coordinates_from_city(city: str, country_hint: Optional[str] = None) -> Optional[Dict[str, Any]]:
    try:
        url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        if not data.get("results"):
            print(f"❌ City not found: {city}")
            return None
        r0 = data["results"][0]
        return {
            "latitude": r0["latitude"],
            "longitude": r0["longitude"],
            "name": r0.get("name", city),
            "country": r0.get("country", country_hint or "Unknown"),
            "timezone": r0.get("timezone", "auto"),
        }
    except Exception as e:
        print(f"❌ Geocoding error: {e}")
        return None


def fetch_archive(latitude: float, longitude: float, start_date: str, end_date: str, timezone: str) -> Optional[Dict[str, Any]]:
    try:
        base = "https://archive-api.open-meteo.com/v1/archive"
        hourly_vars = ["temperature_2m", "windspeed_10m", "weathercode"]
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date,
            "end_date": end_date,
            "hourly": ",".join(hourly_vars),
            "timezone": timezone or "auto",
        }
        resp = requests.get(base, params=params, timeout=60)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"❌ Archive API error: {e}")
        return None


def iter_hourly_records(payload: Dict[str, Any], city: str, country: str) -> List[Dict[str, Any]]:
    hourly = payload.get("hourly", {})
    times: List[str] = hourly.get("time", [])
    temps: List[Optional[float]] = hourly.get("temperature_2m", [])
    winds: List[Optional[float]] = hourly.get("windspeed_10m", [])
    codes: List[Optional[int]] = hourly.get("weathercode", [])

    out: List[Dict[str, Any]] = []
    for idx, ts_str in enumerate(times):
        # ts_str: e.g. "2020-01-01T13:00"
        date_part = ts_str.split("T")[0]
        hour_part = ts_str.split("T")[1][:2] if "T" in ts_str else "00"
        rec = {
            "city": city,
            "country": country,
            "date": date_part,
            "hour": hour_part,
            "event_time": ts_str,
            "weather": {
                "temperature": temps[idx] if idx < len(temps) else None,
                "windspeed": winds[idx] if idx < len(winds) else None,
                "weathercode": codes[idx] if idx < len(codes) else None,
            },
            "source": "open-meteo-archive"
        }
        out.append(rec)
    return out


def main() -> None:
    print("📚 Starting historical weather producer…")
    print(f"📍 City/Country: {CITY}, {COUNTRY}")
    if not START_DATE or not END_DATE:
        sd, ed = compute_default_range()
        print(f"🗓️  Using default 10-year range: {sd} → {ed}")
    else:
        sd, ed = START_DATE, END_DATE
        print(f"🗓️  Using provided range: {sd} → {ed}")

    # Kafka producer connect with retry
    producer = None
    while producer is None:
        try:
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BROKER,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                linger_ms=50,
                acks="1",
            )
            break
        except Exception as e:
            print(f"⏳ Waiting for Kafka… {e}")
            time.sleep(2)

    loc = get_coordinates_from_city(CITY, COUNTRY)
    if not loc:
        sys.exit(1)
    print(f"🗺️  Coordinates: lat={loc['latitude']} lon={loc['longitude']} tz={loc['timezone']}")

    payload = fetch_archive(loc["latitude"], loc["longitude"], sd, ed, loc.get("timezone", "auto"))
    if not payload:
        sys.exit(2)

    records = iter_hourly_records(payload, loc["name"], loc["country"])
    print(f"📦 Preparing to send {len(records)} records → topic={TOPIC}")

    sent = 0
    for rec in records:
        try:
            producer.send(TOPIC, rec)
            sent += 1
            if sent % 1000 == 0:
                print(f"… sent {sent}")
        except Exception as e:
            print(f"❌ send failed: {e}")

    producer.flush()
    print(f"✅ Done. Sent {sent} records.")


if __name__ == "__main__":
    main()


