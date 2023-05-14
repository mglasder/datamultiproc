from pathlib import Path
import pytest as pytest
from assertpy import assert_that

from datamultiproc.sample import BaseSample


def test_save(tmp_path):
    s1 = BaseSample(id="test")
    path = Path(tmp_path) / "test.pkl"

    s1.write_file(path)

    file_exists = path.is_file()
    assert_that(file_exists).is_true()


def test_write_and_read_file(tmp_path):
    s1 = BaseSample(id="test")

    path = Path(tmp_path) / "test.pkl"
    s1.write_file(path)

    s2 = BaseSample.read_file(path=path)

    assert_that(s2).is_equal_to(s1)


def test_write_and_read_file_with_user_defined_sample(tmp_path):
    class Sample(BaseSample):
        data: int

    s1 = Sample(id="test", data=1)

    path = Path(tmp_path) / "test.pickle"
    s1.write_file(path)

    s2 = Sample.read_file(path=path)

    assert_that(s2).is_equal_to(s1)
