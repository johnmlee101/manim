

from constants import *

from mobject.types.vectorized_mobject import VMobject
from mobject.geometry import Rectangle
from mobject.geometry import Line
from mobject.functions import ParametricFunction
from mobject.types.vectorized_mobject import VGroup
from utils.config_ops import digest_config
from utils.color import Color
from utils.paths import alpha_shape
from utils.simple_functions import circular_binary_structure
from scipy import ndimage


class SurroundingRectangle(Rectangle):
    CONFIG = {
        "color": YELLOW,
        "buff": SMALL_BUFF,
    }

    def __init__(self, mobject, **kwargs):
        digest_config(self, kwargs)
        kwargs["width"] = mobject.get_width() + 2 * self.buff
        kwargs["height"] = mobject.get_height() + 2 * self.buff
        Rectangle.__init__(self, **kwargs)
        self.move_to(mobject)


class BackgroundRectangle(SurroundingRectangle):
    CONFIG = {
        "color": BLACK,
        "stroke_width": 0,
        "fill_opacity": 0.75,
        "buff": 0
    }

    def __init__(self, mobject, **kwargs):
        SurroundingRectangle.__init__(self, mobject, **kwargs)
        self.original_fill_opacity = self.fill_opacity

    def pointwise_become_partial(self, mobject, a, b):
        self.set_fill(opacity=b * self.original_fill_opacity)
        return self

    def set_style_data(self,
                       stroke_color=None,
                       stroke_width=None,
                       fill_color=None,
                       fill_opacity=None,
                       family=True
                       ):
        # Unchangable style, except for fill_opacity
        VMobject.set_style_data(
            self,
            stroke_color=BLACK,
            stroke_width=0,
            fill_color=BLACK,
            fill_opacity=fill_opacity
        )
        return self

    def get_fill_color(self):
        return Color(self.color)


class Cross(VGroup):
    CONFIG = {
        "stroke_color": RED,
        "stroke_width": 6,
    }

    def __init__(self, mobject, **kwargs):
        VGroup.__init__(self,
                        Line(UP + LEFT, DOWN + RIGHT),
                        Line(UP + RIGHT, DOWN + LEFT),
                        )
        self.replace(mobject, stretch=True)
        self.set_stroke(self.stroke_color, self.stroke_width)


class SurroundingCurve(ParametricFunction):
    def __init__(self, mob, iterations=5, radius=10, alpha=100, camera=None):
        if camera is None:
            from camera.camera import Camera
            camera = Camera()
        arr = mob.get_binary_array()
        arr = ndimage.binary_dilation(
            arr,
            structure=circular_binary_structure(radius),
            iterations=iterations,
        )
        pixel_list = np.column_stack(np.where(arr == 1)).astype("float64")

        concave_hull = list(alpha_shape(pixel_list, alpha=alpha, only_outer=True))

        # sort edges
        for i, first in enumerate(concave_hull):
            loop = True
            for j, second in enumerate(concave_hull[i + 1:]):
                j += i + 1
                if first[1] == second[0]:
                    loop = False
                    concave_hull[i + 1], concave_hull[j] = \
                        concave_hull[j], concave_hull[i + 1]
            if loop and i != len(concave_hull) - 1:
                warnings.warn(
                    "the alpha shape in split into different parts. This can "
                    "be fixed by increasing alpha."
                )
                print(i, len(concave_hull))
                # breakpoint(context=9)
                pass

        temp = np.zeros((len(concave_hull) + 1, 2))
        for i, pair in enumerate(concave_hull):
            temp[i] = pixel_list[pair[0]]
        temp[-1] = pixel_list[concave_hull[0][0]]
        pixel_list = temp

        point_list = np.zeros((pixel_list.shape[0], pixel_list.shape[1] + 1))
        point_list[:, 0] = pixel_list[:, 0] * camera.frame_height / camera.pixel_height
        point_list[:, 1] = -pixel_list[:, 1] * camera.frame_width / camera.pixel_width
        # TODO: account for quality

        # want this to be 1
        mod = len(point_list) % 3
        if mod == 0:
            point_list = point_list[:-2]
        elif mod == 1:
            pass
        elif mod == 2:
            point_list = point_list[:-1]

        ParametricFunction.__init__(
            self,
            lambda t, point_list=point_list: point_list[int(t)],
            t_min=0,
            t_max=len(point_list) - 1,
            num_anchor_points=(len(point_list) + 2) // 3,
            scale_handle_to_anchor_distances_after_applying_functions=False,
        )
        self.move_to(mob.get_center())
