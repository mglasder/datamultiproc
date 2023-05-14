import time

import pytest
from assertpy import assert_that

from datamultiproc.composer import Compose
from datamultiproc.fileio import Cache, Save
from datamultiproc.processor import Processor


@pytest.fixture
def samples():
    from datamultiproc.sample import BaseSample

    class Sample(BaseSample):
        data: int

    return [Sample(id=f"sample_{i}", data=i) for i in range(5)]


@pytest.fixture
def TestProcessor():
    class TestProcessor(Processor):
        def process(self, sample):
            sample.data = sample.data + 1
            return sample

    return TestProcessor()


@pytest.fixture
def TestProcessorSlow():
    class TestProcessorSlow(Processor):
        wait: int

        def process(self, sample):
            import time

            time.sleep(self.wait)
            sample.data = sample.data + 1
            return sample

    return TestProcessorSlow


def test_save_in_pipeline(tmp_path, samples, TestProcessor):

    process = Compose([TestProcessor, Save(save_to_dir=tmp_path)])

    for sample in samples:
        process(sample)

    path = tmp_path / "TestProcessor"
    files = list(path.iterdir())
    assert_that(len(files)).is_equal_to(len(samples))


def test_cache_in_pipeline(tmp_path, samples, TestProcessor):

    process = Compose([Cache(cache_dir=tmp_path, processor=TestProcessor)])

    for sample in samples:
        process(sample)

    path = tmp_path / "TestProcessor"
    files = list(path.iterdir())
    assert_that(len(files)).is_equal_to(len(samples))


def test_cache_second_iter_is_fast(tmp_path, samples, TestProcessorSlow):

    wait = 1

    process = Compose(
        [
            Cache(
                cache_dir=tmp_path,
                processor=TestProcessorSlow(wait=wait),
            ),
        ]
    )

    tic = time.time()
    for sample in samples:
        process(sample)
    toc = time.time()
    first_iter_time = toc - tic

    tic = time.time()
    for sample in samples:
        process(sample)
    toc = time.time()

    second_iter_time = toc - tic

    assert_that(first_iter_time).is_greater_than(len(samples) * wait)
    assert_that(second_iter_time).is_less_than(1)
