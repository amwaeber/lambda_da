import matplotlib.colors as mc
import colorsys

color_wheel = {0:  "#000000",
               1:  "#2080ff",
               2:  "#40c040",
               3:  "#c00000",
               4:  "#ff8000",
               5:  "#40c0ff",
               6:  "#20ff80",
               7:  "#ff4040",
               8:  "#8040ff",
               9:  "#c0ff40",
               10: "#202080"}

color_names = {0: "black",
               1: "blue",
               2: "green",
               3: "red",
               4: "orange",
               5: "light blue",
               6: "light green",
               7: "light red",
               8: "violet",
               9: "lime",
               10: "purple"}


def lighten_color(color, amount=0.5):
    """
    Lightens the given color by multiplying (1-luminosity) by the given amount.
    Input can be matplotlib color string, hex string, or RGB tuple.

    Examples:
    >> lighten_color('g', 0.3)
    >> lighten_color('#F034A3', 0.6)
    >> lighten_color((.3,.55,.1), 0.5)
    """

    try:
        c = mc.cnames[color]
    except:
        c = color
    c = colorsys.rgb_to_hls(*mc.to_rgb(c))
    return colorsys.hls_to_rgb(c[0], 1 - amount * (1 - c[1]), c[2])
