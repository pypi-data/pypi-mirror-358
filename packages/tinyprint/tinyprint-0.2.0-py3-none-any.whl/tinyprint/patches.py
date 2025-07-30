"""Monkey patches"""

from marko import block

# Allow multiple blank lines to create multiple blank lines


class BlankLine(block.BlockElement):
    """Blank lines"""

    priority = 5

    def __init__(self, start: int) -> None:
        self._anchor = start

    @classmethod
    def match(cls, source) -> bool:
        line = source.next_line()
        return line is not None and not line.strip()

    @classmethod
    def parse(cls, source) -> int:
        m = source.match
        source.consume()
        return m


block.BlankLine = BlankLine
