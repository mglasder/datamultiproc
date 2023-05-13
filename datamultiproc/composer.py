from typing import List


class Compose:
    def __init__(self, transforms: List):
        self.transforms = transforms

    def __call__(self, item):
        for t in self.transforms:
            item = t(item)
        return item
