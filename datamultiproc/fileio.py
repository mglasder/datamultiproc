from pathlib import Path
from datamultiproc.composer import Compose
from datamultiproc.processor import Processor
from datamultiproc.sample import BaseSample
from typing import Union


def get_stagedir(save_dir: Path, stage: str) -> Path:
    return save_dir / stage


def get_filename(id: str, stage: str) -> str:
    return f"{id}_{stage}_.pickle"


class Save(Processor):
    save_to_dir: Union[Path, str]

    def process(self, sample: BaseSample):
        stage = sample.processing_history[-1][0]
        stagedir = get_stagedir(Path(self.save_to_dir), stage)
        filename = get_filename(str(sample.id), stage)
        self._write(sample, stagedir, filename)
        return sample

    def _write(self, sample: BaseSample, stagedir: Path, filename: str):
        stagedir.mkdir(exist_ok=True)
        filepath = stagedir / filename
        sample.write_file(filepath)
        self.logger.info(f"sample saved to: {filepath}")

    def _add_stage_to_history(self, sample: BaseSample) -> BaseSample:
        """Do not add to processing history"""
        return sample


class Cache(Processor):
    cache_dir: Union[Path, str]
    processor: Processor

    @property
    def _save(self):
        return Save(save_to_dir=self.cache_dir)

    @property
    def _process_and_save(self):
        return Compose([self.processor, self._save])

    def process(self, sample: BaseSample):
        stage_name = self.processor.stage[0]
        stagedir = get_stagedir(Path(self.cache_dir), stage_name)
        filename = get_filename(sample.id, stage_name)
        filepath = stagedir / filename
        if filepath.is_file():
            sample = BaseSample.read_file(filepath)
            self.logger.info(f"sample loaded from: {filepath}")
        else:
            sample = self._process_and_save(sample)

        return sample

    def _add_stage_to_history(self, sample: BaseSample) -> BaseSample:
        """Do not add to processing history"""
        return sample
