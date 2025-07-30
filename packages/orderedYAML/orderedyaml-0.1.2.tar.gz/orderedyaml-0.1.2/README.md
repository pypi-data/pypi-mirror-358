# orderedYAML
A small Python package to recursively convert Python dicts/lists into `ruamel.yaml`-compatible, ordered YAML using `CommentedMap`. Preserves formatting, ordering, and supports custom key orders at any nesting depth.

## Features

- Recursively reorders YAML dictionaries based on custom paths
- Outputs block-style YAML using `ruamel.yaml`
- Compatible with Python 3.7+

## Installation

```bash
pip install orderedYAML
```

---
## Usage
```python
from core import OrderedYAML

data = {
    "outerlist": {
        "outeritems": [
            {
                "id": 1,
                "name": "inner-1",
                "inneritems": [
                    {"z": 3, "a": 1, "m": 2},
                    {"a": 4, "z": 5, "m": 6},
                ]
            },
            {
                "id": 2,
                "inneritems": [
                    {"m": 9, "z": 8, "a": 7}
                ],
                "name": "inner-2"
            }
        ]
    }
}

ordering = {
    "outerlist.outeritems[*]": ["name", "id", "inneritems"],
    "outerlist.outeritems[].inneritems[*]": ["z", "m", "a", "q"]
}
oy = OrderedYAML(data, path_ordering=ordering)
print(oy.dumps())
```

Resulting in 
```json
outerlist:
  outeritems:
  - name: inner-1
    id: 1
    inneritems:
    - z: 3
      m: 2
      a: 1
    - z: 5
      m: 6
      a: 4
  - name: inner-2
    id: 2
    inneritems:
    - z: 8
      m: 9
      a: 7
```