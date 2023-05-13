import time
from multiprocessing import Process, Queue
from typing import Optional, List, Callable
import numpy as np

from datamultiproc.composer import Compose
from datamultiproc.processor import Processor, ProcessingError
from datamultiproc.sample import BaseSample


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Point(x={self.x}, y={self.y})"


class Sample(BaseSample):
    name: Optional[str]
    raw_data: Optional[np.ndarray]
    points: Optional[List[Point]]
    area: Optional[float]
    height: Optional[float]


class CreatePointsProcessor(Processor):
    def process(self, sample: Sample):
        raw = sample.raw_data.reshape(-1, 2)
        sample.points = [Point(x, y) for x, y in raw]

        return sample


class CalculateAreaProcess(Processor):
    def process(self, sample: Sample):
        points = sample.points
        area = 0.0
        for i in range(len(points)):
            j = (i + 1) % len(points)
            area += points[i].x * points[j].y
            area -= points[i].y * points[j].x
        area = abs(area) / 2.0

        sample.area = area

        time.sleep(1)

        return sample


def do_processing(process: Callable, queue: Queue):
    while not queue.empty():
        sample = queue.get()
        try:
            sample = process(sample)
        except ProcessingError:
            print(f"failed processing: {sample.id}")


def main():
    topleft = np.array([0, 1])
    topright = np.array([1, 1])
    bottomright = np.array([1, 0])
    bottomleft = np.array([0, 0])

    points = [topleft, topright, bottomright, bottomleft]

    def create_raw_samples(n=10) -> List[Sample]:
        samples = []
        for i in range(n):
            name = f"sample-{i}"

            r_points = [p + np.random.rand(2) * 0.1 for p in points]
            r_points = np.array(r_points).flatten()

            s = Sample(id=str(i), name=name, raw_data=r_points)
            samples.append(s)

        return samples

    process = Compose(
        [
            CreatePointsProcessor(),
            CalculateAreaProcess(),
        ]
    )

    samples_queue = Queue()
    for s in create_raw_samples(10):
        samples_queue.put(s)

    NUM_PROCESSES = 1

    t0 = time.time()
    processes = []
    for _ in range(NUM_PROCESSES):
        p = Process(target=do_processing, args=(process, samples_queue))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()
    t1 = time.time()

    print(f"\ntotal time (process={NUM_PROCESSES}): {t1 - t0}\n")


if __name__ == "__main__":
    main()
