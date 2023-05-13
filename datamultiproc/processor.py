from abc import abstractmethod, ABCMeta

from datamultiproc.sample import Aggregate, BaseSample
from datamultiproc.utils import get_class_name, LoggerMixin


class ProcessingError(Exception):
    pass


class Processor(LoggerMixin, Aggregate, metaclass=ABCMeta):
    class Config:
        underscore_attrs_are_private = True

    @property
    def stage(self):
        return get_class_name(self), str(self)

    @abstractmethod
    def process(self, sample: BaseSample):
        raise NotImplementedError

    def __call__(self, sample: BaseSample) -> BaseSample:
        try:
            sample = self.process(sample)
            sample = self._add_stage_to_history(sample)
            self.logger.info(f"{sample.id}-{self.stage[0]}-done")
        except Exception as e:
            raise ProcessingError(f"{sample.id}-{self.stage[0]}-{e}") from e

        return sample

    def _add_stage_to_history(self, sample: BaseSample) -> BaseSample:
        sample.processing_history.append(self.stage)
        return sample
