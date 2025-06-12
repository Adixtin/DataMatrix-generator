from svg_renderer import svg_from_matrix
from matrix import matrix



class DataMatrix():

    def __init__(self, msg, rect=False,
                 codecs=['ascii', 'C40', 'text', 'X12', 'edifact']):
        self.message = msg
        self.rectangular = rect
        codecs = [c.lower() for c in codecs]
        for codec in codecs:
            if codec not in ['ascii', 'c40', 'text', 'x12', 'edifact']:
                raise TypeError("codec must be one of: 'ascii', 'c40', 'text', 'x12', 'edifact'")

        self.codecs = codecs

    def __repr__(self):
        return f"<DataMatrix: {self.message!r}>"

    def svg(self, fg="#000", bg="fff", margin=1):
        return svg_from_matrix(self.matrix,fg=fg, bg=bg, margin=margin)

    @property
    def matrix(self):
        return matrix(self.message, self.codecs, self.rectangular)