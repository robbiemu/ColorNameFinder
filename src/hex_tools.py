from collections import namedtuple

RGB = namedtuple('RGB', ['r','g','b'])
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return RGB(*(int(hex_color[i:i+2], 16) for i in (0, 2, 4)))

def rgb_to_hex(rgb: RGB):
    return '#{:02x}{:02x}{:02x}'.format(*(map(lambda x: int(round(x)),rgb)))
