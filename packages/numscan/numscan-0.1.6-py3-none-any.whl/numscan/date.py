from datetime import date, timedelta, datetime
from .base import NumberCounter

class DatePatternCounter(NumberCounter):
    def __init__(self, filepath: str, start: date, end: date):
        self.start = start
        self.end = end
        self.formats = [
            "%Y%m%d",  # 20251223
            "%d%m%Y",  # 23122025
            "%d%m%y",  # 231225
            "%m%d%Y",  # 12232025
            "%m%d%y"   # 122325
        ]
        super().__init__(filepath)

    def _generate_numbers(self) -> list[int]:
        numbers = set()
        current = self.start
        while current <= self.end:
            for fmt in self.formats:
                try:
                    number = int(current.strftime(fmt))
                    numbers.add(number)
                except ValueError:
                    pass
            current += timedelta(days=1)
        return sorted(numbers)

    def get_description(self, number: int) -> str:
        str_number = str(number)
        for fmt in self.formats:
            try:
                dt = datetime.strptime(str_number, fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue
        return "Unknown format"