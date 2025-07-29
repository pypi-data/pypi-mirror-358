from .base import NumberCounter

class SquareCounter(NumberCounter):
    def _generate_numbers(self) -> list[int]:
        n = 1
        squares = []
        while (sq := n * n) <= self.limit:
            squares.append(sq)
            n += 1
        return squares