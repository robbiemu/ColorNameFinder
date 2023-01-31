# ColorNameFinder

An artist's color name search tool - given a csv of colors, find the best matching color when considering tint, shade, or tone.

I could use help on the package setup (and in general).

## concept
I was inspired by way artyclick shows colors and allows searching for them. If you look at an individual color, for example [mauve](https://colors.artyclick.com/color-names-dictionary/color-names/mauve-color) you'll notice that it prominently displays the shades, tints, and tones of the color, rather like an artist might like. If you [ask it](https://colors.artyclick.com/color-name-finder/) for the name of a color, it will use a hidden unordered list of about a thousand color names, and some javascript to find the nearest colorname to the color you chose. In fact it will also show alternatives.

I noticed that quite often a shade, tint or tone of an alternative (or even the best match) was often a better match than the color it provided. For those who don't know about shade, tint and tone, there's a nice write up at [Dunn Edward's Paints](https://www.dunnedwards.com/pros/blog/color-terminology-hues-tints-shades-and-tones/). It looks like shade and tint are the same but with signs reversed, if doing this on tuples representing colors. For tone it is different, a negative value would I think saturate the result.

I felt like there must be authoritative (or at least well sourced) colorname sources it could be using.

In terms of the results, since I want any color or its shade/tint/tone, I want a result like this:
```
{'color': '#aabbcc',
 'offset': {'type': 'tint', 'value': 0.31060384614807254}}
```
So I can return the actual color name from the color, plus the type of color transform to get there and the amount of you have to go.

For distance of colors, there is a great algorithm that is meant to model human perception that I am using, called [CIEDE 2000](https://hajim.rochester.edu/ece/sites/gsharma/papers/CIEDE2000CRNAFeb05.pdf). Frankly, I'm just using a snippet I found that implements this, it could be wrong.

So now I want to take in two colors, compare their shade, tint, and tone to a target color, and return the one with the least distance. After I am done, I can reconstruct if it was a shade, tint or tone transform from the result just by running all three once and choosing the best fit. With that structure, I can iterate over every color, and that should do it. I use optimization because I don't want to hard code what offsets it should consider (though I am reconsidering this choice now!).

because I want to consider negatives for tone but not for shade/tint, my objective will have to transform that. I have to include two values to optimize, since the objection function will need to know what color to transform (or else the result will give me know way of knowing which color to use the offset with).

so my call should look something like the following:
```py
result = min(minimize(objective, (i,0), bounds=[(i, i), (-1, 1)]) for i in range(len(colors)))

offset_type = resolve_offset_type(result)
```

## sample usage:

```py
from ColorNameFinder import ColorNameFinder
import requests

url = 'https://unpkg.com/color-name-list/dist/colornames.bestof.min.json'
resp = requests.get(url)
if resp.status_code == 200:
  colors = resp.json()
  cnf = ColorNameFinder(['#' + color[1] for color in colornames])
  result = cnf.nearest_color(sample)
  result['name'] = colors[result.color] 
```

results will look like:
```json
{
  'color': '#acaaaa', 
  'offset': {
    'type': 'shade', 
    'value': 0.07370528284098173
  }
}
```
which should be read as _"a shade of the sample color #acaaaa, transformed towards black by 7%"_.

You can get the actual adjusted hex code of that value from helper functions:
```py
from ColorNameFinder import shade_func, rgb_to_hex

rgb_to_hex(shade_func(result['color'], result['offset']['value']))
```
```
'#999797'
```

## resources

there are assets in the package that include sample csv lists you can use, under sources ([assets/sources](assets/sources) in this project, rather than the build artifact).

details on all provided asset data is provided in a readme.md in each folder.

### meodai/color-names

meodai's great [color-names](https://github.com/meodai/color-names) project has two lists you can use, and it is probably best to use this directly from their project rather than the one included snapshot of best names.

see the [readme](assets/sources/meodai/readme.md) for more information.

### coolors.co

the awesome [coolors](https://coolors.co) project ships with a set of colors: the main one it uses I believe is called _name_ in their data source. snapshots of all their provided datasources are included. 

see the [readme](assets/sources/coolors/readme.md) for more information.
