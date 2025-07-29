from typing import Iterable, Iterator


class StepIterator:
    def __init__(self, delegate: Iterable, steps: int) -> None:
        """
        An iterator that repeats the delegate iterator until the
        specified number of steps is reached.

        :param delegate: An iterable to delegate the iteration to.
        :param steps: The total number of steps to yield items.
        """
        self.steps = steps
        self.delegate = delegate

    def __iter__(self) -> Iterator:
        current_step = 0
        while current_step < self.steps:
            delegate_iterator = iter(self.delegate)
            items_yielded_this_pass = 0
            for item in delegate_iterator:
                yield item
                current_step += 1
                items_yielded_this_pass += 1
                if current_step >= self.steps:
                    break
            if items_yielded_this_pass == 0:
                # If the delegate is empty or exhausted and no items were yielded in this pass,
                # it means we can't make progress.
                break
