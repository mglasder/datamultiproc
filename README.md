# datamultiproc: A Python multiprocessing data pipeline library

Create Processors, compose them into pipelines and process your data using Python's 
multiprocessing library. 

## Concepts

### Sample

A Sample is a data object that is passed through the pipeline.
A custom sample can be simply implemented by inheriting from `BaseSample` and adding 
the desired data fields. Note that an `def __init__(self, ...)` method is not required. 
'BaseSample' is build in top of Pydantics `BaseModel` and inherits its functionality.
For more information, see [Pydantic](https://docs.pydantic.dev/latest/).

Data fields can be of any type and also Optional. The latter is especially handy when they are filled 
during the execution of the pipeline.

```python
import numpy as np
from datamultiproc import BaseSample
from typing import Optional


class CustomSample(BaseSample):
    data: int
    optional_data: Optional[str] = None
    array: np.ndarray
```

`BaseSample` has two special fields (`id` and `processing_history`). 
The first has to be filled during instantiation of a `Sample`, the latter is appended to during execution
of the pipeline, in order to keep track of all processing steps.

```python
class BaseSample(Aggregate):
    processing_history: List[Tuple[str, str]] = []
    id: str
```

### Processor

A `Processor` carries out an actual processing step on a `Sample`. 
To implement a custom `Processor`, you simply inherit from the `Processor`class and implement the `process()` method.

```python
# Processor without arguments
class CustomProcessor(Processor):
    def process(self, sample: Sample) -> Sample:
        # do something with sample, e.g.
        sample.data = sample.date + 1
        return sample

    
# Processor with arguments
class CustomProcessor(Processor):
    step_size: int
    _hidden_arg: int = 1

    def process(self, sample: Sample) -> Sample:
        # do something with sample, e.g.
        sample.data = sample.date + self.step_size + self._hidden_arg
        return sample
```


### Compose

Compose chains multiple `Processor` together. 
They are executed in the order they are passed to the `Compose` constructor.

```python
process = Compose(
    CustomProcessor(),
    CustomProcessor(step_size=2),
    CustomProcessor(step_size=3),
)

samples = [...] # some list of samples

processed_samples = [process(s) for s in samples]
```


### Cache and Save

`Cache` and `Save` are special `Processors` that can be used to store intermediate results.
`Cache` stores `Samples`after the processing step, that it is wrapped around as a '.pickle' file.
The files are stored inside a subfolder of the specified `save_to_dir` folder. 
The subfolder is named after the "Processor" class.
If the pipeline is executed again, `Cache` will first check if the file already exists
and if so, it will load the `Samples` from the file instead of executing the wrapped `Processor` again.

`Save` works similarly, but does not load samples from file, if they already exist.

`Cache` is especially useful for storing intermediate results, that are expensive to compute.
`Save` is useful for storing the final results of a pipeline.

```python
process = Compose(
    Cache(
        processor=CustomProcessor(),
        cache_dir="path/to/cache"
    ),
    CustomProcessor(step_size=2),
    CustomProcessor(step_size=3),
    Save(save_to_dir="path/to/save"),
)
```

## Multiprocessing

The library can be used with Python's `multiprocessing` library, as follows.
A full working example can be found in `example.py`.

```python
from multiprocessing import Process, Queue

# number of processor cores of your machine
NUM_PROCESSES = 8

# list of samples
samples = [...]

process = Compose([SomeProcessor(), 
                   AnotherProcessor(), 
                   Save(save_to_dir="path/to/save"),
                   ])

# put the samples into a multiprocessing Queue
samples_queue = Queue()
for s in samples:
    samples_queue.put(s)
    

def do_processing(process: Callable, queue: Queue):
    while not queue.empty():
        sample = queue.get()
        try:
            sample = process(sample)
        except ProcessingError:
            print(f"failed processing: {sample.id}")
    
processes = []
for _ in range(NUM_PROCESSES):
    p = Process(target=do_processing, args=(process, samples_queue))
    p.start()
    processes.append(p)

for p in processes:
    p.join()



```
