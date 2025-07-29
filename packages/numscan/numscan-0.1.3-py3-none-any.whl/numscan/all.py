from .base import NumberCounter

class IntegerCounter(NumberCounter):
    def _generate_numbers(self) -> list[int]:
        return list(range(1, self.limit + 1))