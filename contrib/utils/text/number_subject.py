from dataclasses import dataclass

ADULT = ("взрослый", "взрослых", "взрослых")
CHILD = ("ребёнок", "ребёнка", "детей")


@dataclass
class NumberSubject:
    n: int
    options: tuple[str]

    @property
    def index(self):
        digits = [int(x) for x in str(self.n)]
        if not (10 < self.n < 20):
            if digits[-1] == 1:
                return 0
            if digits[-1] in [2, 3, 4]:
                return 1
        return 2

    @property
    def subject(self):
        return self.options[self.index]

    @property
    def pair(self):
        return f"{self.n} {self.subject}"


def get_adults(n):
    return NumberSubject(n, ADULT).pair


def get_children(n):
    return "без детей" if n == 0 else \
        NumberSubject(n, CHILD).pair
