from collections import namedtuple

from hex_tools import RGB


def shade_func(color, offset):
    r,g,b = color
    offset *= 255
    return RGB(r - offset, g - offset, b - offset)

def tint_func(color, offset):
    r,g,b = color
    offset *= 255
    return RGB(r + offset, g + offset, b + offset)

ToneComponents=namedtuple('ToneComponents', ['ratio', 'value']) 
def tone_func(color, offset):
    r, g, b = color
    gr = offset.ratio * 255
    gray = RGB(gr, gr, gr)
    return (
        r * (1 - offset.value) + gray.r * offset.value,
        g * (1 - offset.value) + gray.g * offset.value,
        b * (1 - offset.value) + gray.b * offset.value
    )
