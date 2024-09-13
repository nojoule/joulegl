from typing import Any, Dict, List, Tuple

VAR_GROUP_CONFLICT: str = (
    "Can't replace multiple dynamic variables in danymic shader src. Last group: {}, conflicting group: {}"
)


def get_shader_src(path: str) -> str:
    processed_src: str = ""
    with open(path, "r") as src:
        for line in src:
            processed_src = processed_src + line
    return processed_src


class ShaderParser:
    def __init__(self) -> None:
        self.static_var_map: Dict[str, str] = dict()
        self.dynamic_id_var_map: Dict[str, int] = dict()
        self.dynamic_var_map: Dict[str, Tuple[str, List[str]]] = dict()

    def set_static(self, static_vars: Dict[str, Any]) -> None:
        for key, value in static_vars.items():
            self.static_var_map["${}$".format(key)] = str(value)

    def set_dynamic(self, dynamic_vars: Dict[str, Dict[str, List[str]]]) -> None:
        for group, sub_groups in dynamic_vars.items():
            for sub_group, values in sub_groups.items():
                if group in self.dynamic_id_var_map:
                    if self.dynamic_id_var_map[group] != len(values):
                        raise Exception(
                            "Mismatching shader var group size for value: {} not matching {} for {}.".format(
                                len(values), self.dynamic_id_var_map[group], group
                            )
                        )
                else:
                    self.dynamic_id_var_map[group] = len(values)
                self.dynamic_var_map["$${}_{}$$".format(group, sub_group)] = (
                    group,
                    values,
                )

    def process_line(self, line: str) -> str:
        processed_line: str = line

        for static, value in self.static_var_map.items():
            processed_line: str = processed_line.replace(static, value)

        if "$$" in processed_line:
            current_group: str | None = None
            for dynamic, (group, _) in self.dynamic_var_map.items():
                if dynamic in processed_line:
                    if current_group is not None and current_group != group:
                        raise Exception(VAR_GROUP_CONFLICT.format(current_group, group))
                    current_group = group
            if current_group is not None:
                new_lines: str = ""
                current_line: str = processed_line
                for i in range(self.dynamic_id_var_map[current_group]):
                    for dynamic, (group, values) in self.dynamic_var_map.items():
                        if current_group == group:
                            current_line = current_line.replace(dynamic, values[i])
                    new_lines = new_lines + current_line
                    current_line = processed_line
                processed_line = new_lines

        return processed_line.replace("//$$", "").replace("$$", "").replace("//$", "")

    def parse(self, path: str) -> str:
        processed_src: str = ""
        with open(path, "r") as src:
            for line in src:
                processed_src = processed_src + self.process_line(line)
        return processed_src
