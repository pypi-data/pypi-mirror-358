import pytest
from orderedYAML import OrderedYAML
from ruamel.yaml import YAML
from io import StringIO


def test_path_to_dotted():
    oy = OrderedYAML({}, {})
    assert oy._path_to_dotted(('a', 'b', 0, 'c', 1)) == 'a.b[0].c[1]'
    assert oy._path_to_dotted(('outer', 0, 'inner', 2)) == 'outer[0].inner[2]'


def test_extract_key_ordering():
    template = {
        "outer": {
            "item": [
                {
                    "x": None,
                    "y": None,
                    "z": None
                }
            ]
        }
    }

    oy = OrderedYAML({}, ordering_template=template)
    assert oy.key_ordering == {
        (): ["outer"],
        ("outer",): ["item"],
        ("outer", "item", 0): ["x", "y", "z"]
    }


def test_match_order_from_template():
    template = {
        "top": {
            "nested": {
                "c": None,
                "a": None,
                "b": None
            }
        }
    }

    data = {
        "top": {
            "nested": {
                "a": 1,
                "b": 2,
                "c": 3
            }
        }
    }

    oy = OrderedYAML(data, ordering_template=template)
    ordered = oy.dumps()

    assert ordered.index('c: 3') < ordered.index('a: 1') < ordered.index('b: 2')


def test_match_order_from_dot_path_wildcard():
    data = {
        "list": [
            {"z": 3, "a": 1, "m": 2},
            {"m": 5, "a": 2, "z": 4}
        ]
    }

    ordering = {
        "list[*]": ["a", "m", "z"]
    }

    oy = OrderedYAML(data, path_ordering=ordering)
    result = oy.dumps()

    assert "a: 1" in result and "m: 2" in result and "z: 3" in result
    assert result.index("a: 1") < result.index("m: 2") < result.index("z: 3")
    assert result.index("a: 2") < result.index("m: 5") < result.index("z: 4")


def test_dot_path_dict_and_list_wildcard():
    data = {
        "environments": {
            "dev": {
                "services": [
                    {"z": 9, "a": 2, "m": 3}
                ]
            },
            "prod": {
                "services": [
                    {"m": 6, "a": 1, "z": 8}
                ]
            }
        }
    }

    ordering = {
        "environments.*.services[*]": ["a", "m", "z"]
    }

    oy = OrderedYAML(data, path_ordering=ordering)
    result = oy.dumps()

    assert result.index("a: 2") < result.index("m: 3") < result.index("z: 9")
    assert result.index("a: 1") < result.index("m: 6") < result.index("z: 8")


def test_fallback_ordering_if_no_match():
    data = {
        "thing": {
            "c": 1,
            "b": 2,
            "a": 3
        }
    }

    oy = OrderedYAML(data)
    result = oy.dumps()

    # Default ordering should follow insertion (no reordering)
    assert result.index("c: 1") < result.index("b: 2") < result.index("a: 3")
