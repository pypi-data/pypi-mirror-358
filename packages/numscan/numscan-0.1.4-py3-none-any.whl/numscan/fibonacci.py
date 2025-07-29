from .base import NumberCounter

class FibonacciCounter(NumberCounter):
    def _generate_numbers(self) -> list[int]:
        fibs = [1, 2]
        while (n := fibs[-1] + fibs[-2]) <= self.limit:
            fibs.append(n)
        return fibs