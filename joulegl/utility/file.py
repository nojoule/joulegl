import json
import os
from datetime import datetime, timezone
from functools import reduce
from typing import Any, Dict

from .definitions import BASE_PATH
from .singleton import Singleton


class StatsFileHandler(metaclass=Singleton):
    def __init__(self, data_path: str | None = None) -> None:
        self.data_path: str = (
            os.path.join(BASE_PATH, "data") if data_path is None else data_path
        )
        self.stats_cache: Dict[str, Dict[str, Dict[str, Any]]] = dict()
        self.stats_cache["default"] = dict()
        self.day_key: str = datetime.utcfromtimestamp(
            datetime.timestamp(datetime.now().replace(tzinfo=timezone.utc).astimezone())
        ).strftime("%Y-%m-%d")
        os.makedirs(self.data_path, exist_ok=True)
        os.makedirs(os.path.join(self.data_path, "stats"), exist_ok=True)

    def load_statistics(self, app_name: str | None = None) -> None:
        stats_prefix: str = "default" if app_name is None else app_name
        try:
            with open(
                os.path.join(
                    self.data_path, "stats", "%s_%s.json" % (stats_prefix, self.day_key)
                ),
                "r",
            ) as stats_file:
                file_data = stats_file.read()
                if file_data:
                    self.stats_cache[stats_prefix] = json.loads(file_data)
                    for name, stat in self.stats_cache[stats_prefix].items():
                        for time, time_stat_slice in stat.items():
                            assert type(time_stat_slice) != "list"
                            self.stats_cache[stats_prefix][name][time] = [
                                time_stat_slice
                            ]
        except FileNotFoundError:
            with open(
                os.path.join(
                    self.data_path, "stats", "%s_%s.json" % (stats_prefix, self.day_key)
                ),
                "w+",
            ):
                pass

    def append_statistics(
        self, data: Dict[str, Any], app_name: str | None = None
    ) -> None:
        stats_prefix: str = "default" if app_name is None else app_name
        if stats_prefix not in self.stats_cache.keys():
            self.stats_cache[stats_prefix] = dict()

        time_key: str = datetime.utcfromtimestamp(
            datetime.timestamp(datetime.now().replace(tzinfo=timezone.utc).astimezone())
        ).strftime("%Y-%m-%d %H:%M:%S")

        for name, stat in data.items():
            if name not in self.stats_cache[stats_prefix].keys():
                self.stats_cache[stats_prefix][name] = dict()
            if time_key not in self.stats_cache[stats_prefix][name].keys():
                self.stats_cache[stats_prefix][name][time_key] = [stat]
            else:
                self.stats_cache[stats_prefix][name][time_key].append(stat)

    def write_statistics(self, app_name: str | None = None) -> None:
        stats_prefix: str = "default" if app_name is None else app_name
        if stats_prefix in self.stats_cache.keys():
            for name, stat in self.stats_cache[stats_prefix].items():
                for time, time_stat_slice in stat.items():
                    if len(time_stat_slice) == 1:
                        self.stats_cache[stats_prefix][name][time] = time_stat_slice[0]
                    else:
                        self.stats_cache[stats_prefix][name][time] = reduce(
                            lambda a, b: a + b, time_stat_slice
                        ) / len(time_stat_slice)

            with open(
                os.path.join(
                    self.data_path, "stats", "%s_%s.json" % (stats_prefix, self.day_key)
                ),
                "w",
            ) as stats_file:
                stats_file.write(json.dumps(self.stats_cache[stats_prefix]))


class DictFile:
    def __init__(self, name: str, sub_path: str, data_path: str | None = None) -> None:
        self.directory_path: str = os.path.join(
            os.getcwd() if data_path is None else data_path, sub_path
        )
        if not os.path.exists(self.directory_path):
            os.makedirs(self.directory_path)
        self.name = name
        self.file_path: str = os.path.join(self.directory_path, "%s.json" % self.name)

    def read_data(self, data: Dict) -> Dict:
        read_data = dict()
        try:
            with open(self.file_path, "r") as stats_file:
                file_data = stats_file.read()
                if file_data:
                    read_data = json.loads(file_data)
        except FileNotFoundError:
            pass
        for key in read_data.keys():
            data[key] = read_data[key]
        return data

    def write_data(self, data: Dict) -> None:
        with open(self.file_path, "w+") as file_data:
            json.dump(data, file_data, sort_keys=True, indent=4)
