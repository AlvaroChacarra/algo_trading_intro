"""Regression contract for the deterministic matching fuzz harness."""

import json

import pytest

from _build.fuzz_matching import (
    DEFAULT_CASES,
    INVALID_MUTATIONS,
    SCHEMA,
    main,
    run_fuzz,
)


ZERO_INVARIANTS = (
    "accepted_invalid_mutations",
    "fill_identity_violations",
    "fok_noop_violations",
    "fok_partials",
    "non_atomic_rejections",
    "output_invariant_violations",
    "overfills",
)


def test_matching_fuzz_is_deterministic_and_preserves_invariants():
    first = run_fuzz(seed=20260828, cases=2_000)
    second = run_fuzz(seed=20260828, cases=2_000)

    assert first == second
    assert first["schema"] == SCHEMA
    assert first["success"] + first["rejected"] == first["cases"]
    # Tightening a representability policy may legitimately move cases from
    # success to fail-closed.  Determinism and the zero-violation invariants are
    # the stable contract, not one particular acceptance ratio.
    assert first["success"] > 0
    assert first["rejected"] > 0
    assert all(first[name] == 0 for name in ZERO_INVARIANTS)
    assert first["ok"] is True
    # This freezes corpus generation while deliberately leaving the
    # success/rejection boundary free to tighten with the numeric policy.
    assert first["case_digest_sha256"] == (
        "cc64eb465f48feb72b3d98947c3eadbd3268dd94f629540ac1a9e6154fe0fd09"
    )
    assert INVALID_MUTATIONS <= set(first["mutation_counts"])
    assert DEFAULT_CASES == 120_000


def test_matching_fuzz_cli_emits_stable_machine_readable_evidence(capsys):
    assert main(["--seed", "20260828", "--cases", "100"]) == 0
    first_line = capsys.readouterr().out
    assert main(["--seed", "20260828", "--cases", "100"]) == 0
    second_line = capsys.readouterr().out

    assert first_line == second_line
    payload = json.loads(first_line)
    assert payload["schema"] == SCHEMA
    assert payload["seed"] == 20260828
    assert payload["cases"] == 100
    assert payload["success"] + payload["rejected"] == 100
    assert all(payload[name] == 0 for name in ZERO_INVARIANTS)
    assert payload["ok"] is True


@pytest.mark.parametrize(
    "kwargs, message",
    [
        ({"seed": True, "cases": 1}, "seed"),
        ({"seed": 1, "cases": True}, "cases"),
        ({"seed": 1, "cases": 0}, "cases"),
    ],
)
def test_matching_fuzz_rejects_ambiguous_or_empty_runs(kwargs, message):
    with pytest.raises(ValueError, match=message):
        run_fuzz(**kwargs)
