from scipy.optimize import minimize
from skimage.color import deltaE_ciede2000

from hex_tools import hex_to_rgb, rgb_to_hex
from color_transforms import shade_func, tint_func, tone_func, ToneComponents


class ColorNameFinder:
  """ColorNameFinder

  An artist's color name search tool - given a csv of colors, find the best matching color when considering tint, shade, or tone.

  sample usage:

  import ColorNameFinder
  import requests

  url = 'https://unpkg.com/color-name-list/dist/colornames.bestof.min.json'
  resp = requests.get(url)
  if resp.status_code == 200:
    colors = resp.json()
    cnf = ColorNameFinder(['#' + color[1] for color in colornames])
    result = cnf.nearest_color(sample)
    result['name'] = colors[result.color] 
  """

  def __init__(self, colors, distance=None):
    if distance is None:
      distance = deltaE_ciede2000
    self.distance = distance

    self.colors = [hex_to_rgb(color) for color in colors]

  def __factory_objective(self, target, preprocessor=lambda x: x):
    def fn(x):
      x = preprocessor(x)
      color = self.colors[x[0]]
      offset, ratio = x[1], x[2]
      bound_offset = abs(offset)
      offsets = [
        shade_func(color, bound_offset), 
        tint_func(color, bound_offset), 
        tone_func(color, ToneComponents(ratio=ratio, value=offset))]
      least_error = min([(right, self.distance(target, right)) \
        for right in offsets], key = lambda x: x[1])[1]   
      return least_error

    return fn
  
  def __resolve_offset_type(self, sample, target, offset, ratio):
    bound_offset = abs(offset) 

    shade = shade_func(sample, bound_offset)
    tint = tint_func(sample, bound_offset)
    tone = tone_func(sample, ToneComponents(ratio=ratio, value=offset))

    lookup = {}
    lookup[shade] =  "shade"
    lookup[tint] =  "tint"
    lookup[tone] =  "tone"

    offsets = [shade, tint, tone]
    least_error = min([(right, self.distance(target, right)) for right in offsets], key = lambda x: x[1])[0]   

    return lookup[least_error]

  def nearest_color(self, target):
    target = hex_to_rgb(target)

    preprocessor=lambda x: (int(x[0]), x[1], x[2])
    objective = self.__factory_objective(target, preprocessor=preprocessor)
    search = [minimize( objective, 
                        (i, 0, 0),
                        bounds=[(i, i), (-1, 1), (0, 1)],
                        method='Powell') \
              for i, color in enumerate(self.colors)]
    best = min(search, key=lambda x: x.fun)
    indices = [i for i, v in enumerate(search) if v.fun == best.fun]
    index = min(indices, \
      key=lambda j: search[j].x[1])
    result = search[index]

    color_index = int(result.x[0])
    nearest_color = self.colors[color_index]
    _, offset, ratio = preprocessor(result.x)
  
    offset_type = self.__resolve_offset_type(nearest_color, target, offset, ratio)

    report = {
      "color": rgb_to_hex(nearest_color),
      "offset": {
        "type": offset_type,
        "value": offset if offset_type == 'tone' else abs(offset)
      }
    }
    if offset_type == 'tone':
      report["offset"]["white ratio"] = ratio

    return report
