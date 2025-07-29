from .base import NumberCounter

class PrimeCounter(NumberCounter):
    def _generate_numbers(self) -> list[int]:
        primes = []
        for num in range(2, self.limit + 1):
            if all(num % p != 0 for p in primes):
                primes.append(num)
        return primes