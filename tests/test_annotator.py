import pytest
from envdiff.comparator import compare
from envdiff.annotator import annotate, AnnotatedKey


@pytest.fixture
def envs():
    first = {"A": "1", "B": "2", "C": "3"}
    second = {"A": "1", "B": "99", "D": "4"}
    return first, second


@pytest.fixture
def annotation(envs):
    first, second = envs
    diff = compare(first, second)
    return annotate(first, second, diff)


def test_all_keys_present(annotation, envs):
    first, second = envs
    all_keys = set(first) | set(second)
    assert set(annotation.entries.keys()) == all_keys


def test_ok_key(annotation):
    entry = annotation.entries["A"]
    assert entry.status == "ok"
    assert entry.value == "1"
    assert entry.other_value == "1"


def test_mismatch_key(annotation):
    entry = annotation.entries["B"]
    assert entry.status == "mismatch"
    assert entry.value == "2"
    assert entry.other_value == "99"


def test_missing_in_second(annotation):
    entry = annotation.entries["C"]
    assert entry.status == "missing_in_second"
    assert entry.value == "3"
    assert entry.other_value is None


def test_missing_in_first(annotation):
    entry = annotation.entries["D"]
    assert entry.status == "missing_in_first"
    assert entry.value is None
    assert entry.other_value == "4"


def test_by_status_ok(annotation):
    ok_entries = annotation.by_status("ok")
    assert len(ok_entries) == 1
    assert ok_entries[0].key == "A"


def test_by_status_mismatch(annotation):
    mismatches = annotation.by_status("mismatch")
    assert len(mismatches) == 1
    assert mismatches[0].key == "B"


def test_by_status_missing_in_second(annotation):
    missing = annotation.by_status("missing_in_second")
    assert len(missing) == 1
    assert missing[0].key == "C"


def test_by_status_missing_in_first(annotation):
    missing = annotation.by_status("missing_in_first")
    assert len(missing) == 1
    assert missing[0].key == "D"


def test_identical_envs_all_ok():
    env = {"X": "1", "Y": "2"}
    diff = compare(env, env)
    result = annotate(env, env, diff)
    assert all(e.status == "ok" for e in result.entries.values())
