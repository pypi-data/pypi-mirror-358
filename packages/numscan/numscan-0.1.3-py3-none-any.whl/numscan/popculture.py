from .base import NumberCounter

class PopCultureCounter(NumberCounter):
    def _generate_numbers(self) -> list[int]:
        return [7, 13, 23, 42, 69, 99, 101, 666, 1337]