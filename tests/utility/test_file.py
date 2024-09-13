import os

import pytest

from joulegl.utility.definitions import BASE_PATH
from joulegl.utility.file import DictFile, StatsFileHandler

STATS_PATH = os.path.join(BASE_PATH, "data", "stats")


@pytest.mark.parametrize("stat_count", [1, 10])
def test_stats_file_handler(stat_count: int) -> None:
    test_value = 234
    container_name = f"test_container_{stat_count}"
    stats_file_handler: StatsFileHandler = StatsFileHandler()
    for _ in range(stat_count):
        stats_file_handler.append_statistics({"test": 234}, container_name)

    found_stats = 0
    for key, values in stats_file_handler.stats_cache[container_name]["test"].items():
        for value in values:
            if test_value == value:
                found_stats += 1
    assert found_stats == stat_count

    file_count = 0
    for filename in os.listdir(STATS_PATH):
        if f"{container_name}_" in filename:
            file_count += 1
    assert file_count == 0
    stats_file_handler.write_statistics(container_name)
    for filename in os.listdir(STATS_PATH):
        if f"{container_name}_" in filename:
            file_count += 1
    assert file_count == 1

    stats_file_handler.stats_cache[container_name] = dict()
    stats_file_handler.load_statistics(container_name)

    found_stats = 0
    for key, values in stats_file_handler.stats_cache[container_name]["test"].items():
        for value in values:
            if test_value == value:
                found_stats += 1
    assert found_stats == 1


def test_dict_file() -> None:
    assert not os.path.exists("tests/tmp/dict")
    dict_file = DictFile("test", "tests/tmp/dict")
    assert os.path.exists("tests/tmp/dict")
    assert not os.path.exists("tests/tmp/dict/test.json")

    empty_data = dict()
    load_empty_data = dict_file.read_data(empty_data)
    assert dict() == load_empty_data

    data = {"test": 234}
    dict_file.write_data(data)
    assert os.path.exists("tests/tmp/dict/test.json")

    loaded_data = dict_file.read_data(empty_data)
    assert loaded_data == empty_data
    assert loaded_data == data


def test_dict_read_empty_file() -> None:
    dict_file = DictFile("test_empty", "tests/tmp/dict")

    with open(dict_file.file_path, "w") as file:
        file.write("")

    empty_data = dict()
    load_empty_data = dict_file.read_data(empty_data)
    assert dict() == load_empty_data
