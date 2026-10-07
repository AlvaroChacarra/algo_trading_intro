"""Lector proporcionado: abre el día publicado sin transformar sus niveles."""
import json
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent / 'data' / 'binance-btcusdt-2022-01-24.ndjson'


def read_snapshots():
    """Devuelve 24 diccionarios nuevos, uno por línea; no filtra ni ordena."""
    with DATA_PATH.open(encoding='utf-8') as stream:
        return [json.loads(line) for line in stream if line.strip()]
