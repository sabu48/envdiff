import os
import pytest
from envdiff.templater import (
    TemplateResult,
    build_template,
    save_template,
    load_template_keys,
)


@pytest.fixture
def tmp(tmp_path):
    return tmp_path


def test_build_template_collects_all_keys():
    a = {"FOO": "1", "BAR": "2"}
    b = {"BAR": "x", "BAZ": "y"}
    result = build_template(a, b)
    assert set(result.keys) == {"FOO", "BAR", "BAZ"}


def test_build_template_sorted_by_default():
    a = {"ZEBRA": "1", "ALPHA": "2", "MANGO": "3"}
    result = build_template(a)
    assert result.keys == sorted(result.keys)


def test_build_template_unsorted():
    a = {"B": "1", "A": "2"}
    result = build_template(a, sort_keys=False)
    assert result.keys == ["B", "A"]


def test_render_no_placeholder():
    result = TemplateResult(keys=["FOO", "BAR"])
    rendered = result.render()
    assert "FOO=" in rendered
    assert "BAR=" in rendered


def test_render_with_placeholder():
    result = TemplateResult(keys=["SECRET"])
    rendered = result.render(placeholder="CHANGEME")
    assert "SECRET=CHANGEME" in rendered


def test_render_with_descriptions():
    result = TemplateResult(
        keys=["API_KEY"],
        descriptions={"API_KEY": "Your API key"},
    )
    rendered = result.render()
    assert "# Your API key" in rendered
    assert "API_KEY=" in rendered


def test_save_and_load_roundtrip(tmp):
    path = str(tmp / "out.env.template")
    result = build_template({"FOO": "1", "BAR": "2"})
    save_template(result, path, placeholder="TODO")
    assert os.path.exists(path)
    keys = load_template_keys(path)
    assert set(keys) == {"FOO", "BAR"}


def test_load_template_keys_skips_comments(tmp):
    path = str(tmp / "t.env")
    with open(path, "w") as fh:
        fh.write("# comment\nFOO=\n\nBAR=val\n")
    keys = load_template_keys(path)
    assert keys == ["FOO", "BAR"]


def test_single_env_template():
    env = {"X": "1"}
    result = build_template(env)
    assert result.keys == ["X"]
