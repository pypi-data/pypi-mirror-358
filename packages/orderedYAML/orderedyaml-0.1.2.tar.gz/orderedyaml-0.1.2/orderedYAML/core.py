from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap
from typing import Any, Dict, List, Tuple, Union
import re


class OrderedYAML:
    """
    A class for dumping YAML with custom key ordering using either:
    - an example structure (`ordering_template`), or
    - dot-path-based key ordering (`path_ordering`), including support for wildcards.

    Supports wildcards:
    - '[]' or '[*]' to match any list index
    - '.*' to match any key at a given level
    """

    def __init__(
        self,
        data: dict,
        ordering_template: dict = None,
        path_ordering: Dict[str, List[str]] = None,
    ):
        """
        Initialize the OrderedYAML instance.

        Args:
            data (dict): The raw data to render as YAML.
            ordering_template (dict, optional): An example structure that defines key ordering.
            path_ordering (dict, optional): A dict using dot-notation to define ordering rules.
                                            Example: {"outer.a[].b[*]": ["x", "y", "z"]}
        """
        self.data = data
        self.yaml = YAML()
        self.yaml.default_flow_style = False
        self.key_ordering = {}

        if ordering_template:
            self.key_ordering = self._extract_key_ordering(ordering_template)
        if path_ordering:
            self.path_ordering_patterns = self._build_path_patterns(path_ordering)
        else:
            self.path_ordering_patterns = []

    def _extract_key_ordering(
        self, node: Any, path: Tuple = ()
    ) -> Dict[Tuple, List[str]]:
        """
        Recursively extract key ordering from an example template.
        """
        ordering = {}
        if isinstance(node, dict):
            ordering[path] = list(node.keys())
            for key, value in node.items():
                ordering.update(self._extract_key_ordering(value, path + (key,)))
        elif isinstance(node, list) and node:
            ordering.update(self._extract_key_ordering(node[0], path + (0,)))
        return ordering

    def _build_path_patterns(
        self, path_ordering: Dict[str, List[str]]
    ) -> List[Tuple[re.Pattern, List[str]]]:
        """
        Convert dot-paths like 'a.b[].c' or 'a.*.c' into compiled regex patterns.

        Returns:
            List of tuples: (compiled regex pattern, key order)
        """
        patterns = []
        for dot_path, key_list in path_ordering.items():
            # Escape special characters
            regex_str = re.escape(dot_path)

            # Handle list wildcards: [] or [*]
            regex_str = regex_str.replace(r"\[\]", r"\[\d+\]")
            regex_str = regex_str.replace(r"\[\*\]", r"\[\d+\]")

            # Handle dict wildcards: .*
            regex_str = regex_str.replace(r"\.\*", r"\.[^.\[\]]+")

            # Final pattern
            pattern = re.compile(f"^{regex_str}$")
            patterns.append((pattern, key_list))
        return patterns

    def _path_to_dotted(self, path: Tuple) -> str:
        """
        Convert tuple path like ('a', 'b', 0, 'c') to dot notation: 'a.b[0].c'
        """
        dotted = []
        for part in path:
            if isinstance(part, int):
                dotted[-1] += f"[{part}]"
            else:
                dotted.append(str(part))
        return ".".join(dotted)

    def _match_order(self, path: Tuple) -> Union[List[str], None]:
        """
        Return key ordering list if a regex pattern matches the path.
        """
        dotted_path = self._path_to_dotted(path)
        for pattern, key_list in self.path_ordering_patterns:
            if pattern.match(dotted_path):
                return key_list
        return self.key_ordering.get(path)

    def _to_ordered_commented_map(
        self, node: Any, path: Tuple = ()
    ) -> Union[CommentedMap, List, Any]:
        """
        Recursively convert data to a CommentedMap with ordered keys.
        """
        if isinstance(node, dict):
            ordered = CommentedMap()
            keys = self._match_order(path) or list(node.keys())
            for key in keys:
                if key in node:
                    ordered[key] = self._to_ordered_commented_map(
                        node[key], path + (key,)
                    )
            return ordered

        elif isinstance(node, list):
            return [
                self._to_ordered_commented_map(item, path + (i,))
                for i, item in enumerate(node)
            ]

        else:
            return node

    def dump(self, fp):
        """
        Write YAML output to a file-like object.

        Args:
            fp: File-like object with .write().
        """
        self.yaml.dump(self._to_ordered_commented_map(self.data), fp)

    def dumps(self) -> str:
        """
        Return YAML as a string.

        Returns:
            str: YAML-formatted string with ordered keys.
        """
        from io import StringIO

        stream = StringIO()
        self.dump(stream)
        return stream.getvalue()
