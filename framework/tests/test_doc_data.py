"""Regresión de los data-builders de los docs: claves y sanidad de los números
que se embeben en las páginas. Si el motor o el CSV cambian y esto pasa, los
documentos siguen contando la verdad."""

import importlib.util
import os

import pytest

HERE = os.path.dirname(__file__)
DOCS = os.path.join(HERE, "..", "_build", "docs")

EXPECTED_KEYS = {
    7: {"snaps", "mids", "imbs", "signalUps", "signalTotal", "mid0"},
    8: {"bids", "asks", "mid", "sweeps", "variants", "big", "limPx"},
    9: {"equity", "fills", "filled", "steps", "finalEquity"},
    10: {"buyonce", "imbalance"},
    11: {"signal", "monos", "monoFinals", "arrivalMid", "avgSlip", "nSlips"},
    12: {"total", "mid0", "sweepAvg", "twapAvg", "vwapAvg", "bars"},
    13: {"skew", "noskew"},
    14: {"naive", "as", "sweep", "sigma", "kappa", "horizon"},
}


def load(n):
    spec = importlib.util.spec_from_file_location(
        f"d{n}", os.path.join(DOCS, f"{n:02d}_data.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.build()


@pytest.fixture(scope="module")
def data():
    return {n: load(n) for n in EXPECTED_KEYS}


def test_builders_expose_expected_keys(data):
    for n, keys in EXPECTED_KEYS.items():
        assert keys <= set(data[n]), f"doc {n}: faltan claves {keys - set(data[n])}"


def test_l7_series_aligned(data):
    d = data[7]
    assert len(d["mids"]) == len(d["imbs"]) == len(d["snaps"]) == 500
    assert 0 < d["signalUps"] <= d["signalTotal"]


def test_l8_slippage_monotone_with_size(data):
    slips = [s["slip"] for s in data[8]["sweeps"]]
    assert slips == sorted(slips), "más tamaño nunca puede dar menos slippage"
    assert data[8]["variants"]["fok"]["nfills"] == 0


def test_l9_fills_complete_and_marked(data):
    d = data[9]
    assert d["filled"] == pytest.approx(0.5, abs=1e-6)
    assert all(0 <= f["i"] < len(d["equity"]) for f in d["fills"])


def test_l12_sweep_worse_than_sliced(data):
    d = data[12]
    assert d["sweepAvg"] < d["twapAvg"] and d["sweepAvg"] < d["vwapAvg"], \
        "vender de golpe debe salir peor que troceado en este dataset"
    assert sum(d["bars"]) == pytest.approx(1.0, abs=1e-3)


def test_l13_skew_tames_inventory(data):
    d = data[13]
    assert d["skew"]["maxInv"] < d["noskew"]["maxInv"]


def test_l14_gamma_monotone_inventory(data):
    inv = [s["maxInv"] for s in data[14]["sweep"]]
    assert inv == sorted(inv, reverse=True), "más gamma => inventario máximo no crece"
