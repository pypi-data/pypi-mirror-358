from collections import deque
from itertools import chain


def reduce_ex(
        function,
        elements,
        n=2,
        prefix=(),
        suffix=(),
):
    """Sliding window reducer that applies function and keeps results in queue.

    Args:
        function: Callable to apply to each window of elements
        elements: Main iterable to process
        n: Window size (must be ≥ 2)
        prefix: Elements to prepend before processing
        suffix: Elements to append after processing

    Yields:
        Results of applying the function to each window
    """
    if not callable(function):
        raise TypeError('function must be callable')

    if n < 2:
        raise ValueError('n must be an int greater than or equal to 2')

    argument_deque = deque(maxlen=n)

    for element in chain(prefix, elements, suffix):
        argument_deque.append(element)
        if len(argument_deque) == n:
            function_call_result = function(*argument_deque)
            yield function_call_result
            argument_deque.clear()
            argument_deque.append(function_call_result)
