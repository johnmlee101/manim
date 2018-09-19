import itertools
import operator
import random
import time

from animation.composition import AnimationGroup
from animation.composition import Succession
from animation.creation import ShowCreation
from animation.creation import Write
from animation.creation import FadeOut
from animation.transform import ApplyMethod
from animation.transform import ReplacementTransform
from animation.update import UpdateFromAlphaFunc
from constants import *
from continual_animation.update import ContinualUpdateFromTimeFunc
from continual_animation.update import ContinualUpdate
from mobject.geometry import Circle
from mobject.geometry import Dot
from mobject.geometry import Line
from mobject.mobject import Group
from mobject.numbers import Integer

from mobject.svg.tex_mobject import TextMobject
from scene.scene import Scene
from utils.rate_functions import linear


def euler_tour(G, start_point):
    ret = [start_point]
    unvisited = set(G.submobjects)
    random.seed(time.time())
    while unvisited:
        next_edge_candidates = [
            line for line in unvisited
            if np.allclose(line.get_start(), ret[-1]) or
            np.allclose(line.get_end(), ret[-1])
        ]
        if next_edge_candidates:
            next_edge = random.choice(next_edge_candidates)
            unvisited.remove(next_edge)
            ret.append(
                next_edge.get_start()
                if np.allclose(next_edge.get_end(), ret[-1])
                else next_edge.get_end()
            )
        else:
            subgraph = Group()
            for edge in unvisited:
                subgraph.add(edge)
            start_point = None
            splice_index = None
            for start_index, point in enumerate(ret):
                for edge in unvisited:
                    if np.allclose(edge.get_start(), point) or \
                            np.allclose(edge.get_end(), point):
                        start_point = point
                        splice_index = start_index
            assert(start_point is not None)
            splice = euler_tour(subgraph, start_point)
            to_remove = set()
            for i in range(len(splice) - 1):
                for edge in unvisited:
                    u, v = edge.get_start_and_end()
                    if np.allclose(u, splice[i]) and np.allclose(v, splice[i + 1]) or \
                            np.allclose(u, splice[i + 1]) and np.allclose(v, splice[i]):
                        to_remove.add(edge)
            for x in to_remove:
                unvisited.remove(x)
            ret = ret[:splice_index] + splice + ret[splice_index + 1:]
            return ret
    return ret


def make_cube():
    points = [p for p in itertools.product([0, 1], repeat=3)]
    lines = [
        (p1, p2)
        for (p1, p2) in itertools.product(points, points)
        if sum(map(operator.xor, p1, p2)) == 1 and p1 < p2
    ]
    mobs = [Line(p1, p2, stroke_width=4) for (p1, p2) in lines]
    return Group(*mobs)


def make_hypercube():
    outer_cube = make_cube()
    inner_cube = make_cube().scale(1. / 3)
    hypercube = Group(*outer_cube.submobjects + inner_cube.submobjects)
    seen_edges = set()
    for inner_edge, outer_edge in \
            zip(inner_cube.submobjects, outer_cube.submobjects):
        inner_start_and_end = list(map(tuple, inner_edge.get_start_and_end()))
        outer_start_and_end = list(map(tuple, outer_edge.get_start_and_end()))

        start_pair = (inner_start_and_end[0], outer_start_and_end[0])
        if start_pair not in seen_edges:
            seen_edges.add(start_pair)
            starting_connecting_line = \
                Line(start_pair[0], start_pair[1], stroke_width=4)
            hypercube.add(starting_connecting_line)

        end_pair = (inner_start_and_end[1], outer_start_and_end[1])
        if end_pair not in seen_edges:
            seen_edges.add(end_pair)
            ending_connecting_line = \
                Line(end_pair[0], end_pair[1], stroke_width=4)
            hypercube.add(ending_connecting_line)
    return hypercube


def rotate_mob(mob, theta, axis=Y_AXIS):
    mob.rotate_about_origin(theta, axis=axis)


def flip_line(line):
    start, end = line.get_start_and_end()
    return Line(end, start, stroke_width=4)


class OpeningScene(Scene):
    def rotate_shape(self):

        hypercube = make_hypercube()
        hypercube.scale(3)
        hypercube.rotate(-PI / 4, Y_AXIS)
        hypercube.rotate(-np.arctan(np.sqrt(2)), X_AXIS)
        hypercube.move_to(ORIGIN).shift(0.7 * UP)
        self.add(hypercube)
        self.wait(0.1)

        def move_along_line(i, start_point=None):
            def place_along_line_from_start(mob, t):
                line = hypercube.submobjects[i]
                vec = line.get_vector()
                mob.move_to(line.get_start() + vec * t)

            def place_along_line_from_end(mob, t):
                line = hypercube.submobjects[i]
                vec = -1 * line.get_vector()
                mob.move_to(line.get_end() + vec * t)

            line = hypercube.submobjects[i]
            if start_point is None:
                start_point = line.get_start()
            if np.allclose(start_point, line.get_start()):
                return place_along_line_from_start
            elif np.allclose(start_point, line.get_end()):
                return place_along_line_from_end

        path_points = euler_tour(
            hypercube,
            hypercube.submobjects[10].get_end()
        )
        print(path_points)
        cur_path_index = 1
        path_edge_indices = []
        while cur_path_index < len(path_points):
            prev_point = path_points[cur_path_index - 1]
            next_point = path_points[cur_path_index]
            for i, edge in enumerate(hypercube.submobjects):
                start, end = edge.get_start_and_end()
                if np.allclose(start, prev_point) and \
                   np.allclose(end, next_point) or \
                   np.allclose(end, prev_point) and \
                   np.allclose(start, next_point):
                    path_edge_indices.append(i)
                    cur_path_index += 1

        point = Circle(
            radius=0.1,
            fill_opacity=1,
            color="#FF0022"
        ).move_to(path_points[0])
        self.bring_to_back(point)

        successions = []
        for point_index, edge_index in enumerate(path_edge_indices):
            point_anim = UpdateFromAlphaFunc(
                point,
                move_along_line(
                    edge_index,
                    start_point=path_points[point_index]
                ),
                rate_func=linear
            )
            color_anim = ApplyMethod(
                hypercube.submobjects[edge_index].set_color,
                RED,
            )
            successions.append(
                AnimationGroup(point_anim, color_anim, run_time=0.1094)  # ???
            )
        point.move_to(path_points[0])
        successions.append(FadeOut(point, run_time=0.7))

        title = TextMobject("Euler Tour").scale(3).shift(2.8 * DOWN)

        run_time = 14. / 12 * PI - 0.015  # hq
        # run_time = 14. / 12 * PI + 0.005
        self.add(ContinualUpdateFromTimeFunc(
            hypercube,
            rotate_mob,
            start_up_time=0,
            wind_down_time=1.0,
            end_time=run_time,
        ))

        self.play(
            Succession(*successions, add_finished_mobjects=False),
            Write(title, run_time=run_time),
        )
        self.wait(0.5)
        self.play(
            FadeOut(hypercube),
            FadeOut(title),
        )

    def construct(self):
        self.rotate_shape()


class ClosingSceneOverlay(Scene):
    def construct(self):
        hypercube = make_hypercube()
        hypercube.scale(3)
        hypercube.rotate(-PI / 4, Y_AXIS)
        hypercube.rotate(-np.arctan(np.sqrt(2)), X_AXIS)
        hypercube.move_to(ORIGIN)

        hypercube.submobjects[3] = flip_line(hypercube.submobjects[3])
        hypercube.submobjects[5] = flip_line(hypercube.submobjects[5])
        hypercube.submobjects[6] = flip_line(hypercube.submobjects[6])
        hypercube.submobjects[7] = flip_line(hypercube.submobjects[7])
        hypercube.submobjects[10] = flip_line(hypercube.submobjects[10])
        hypercube.submobjects[11] = flip_line(hypercube.submobjects[11])
        hypercube.submobjects[17] = flip_line(hypercube.submobjects[17])
        hypercube.submobjects[18] = flip_line(hypercube.submobjects[18])
        hypercube.submobjects[19] = flip_line(hypercube.submobjects[19])
        hypercube.submobjects[21] = flip_line(hypercube.submobjects[21])
        hypercube.submobjects[22] = flip_line(hypercube.submobjects[22])
        hypercube.submobjects[23] = flip_line(hypercube.submobjects[23])
        hypercube.submobjects[24] = flip_line(hypercube.submobjects[24])
        hypercube.submobjects[25] = flip_line(hypercube.submobjects[25])
        hypercube.submobjects[26] = flip_line(hypercube.submobjects[26])
        hypercube.submobjects[27] = flip_line(hypercube.submobjects[27])
        hypercube.submobjects[28] = flip_line(hypercube.submobjects[28])
        hypercube.submobjects[29] = flip_line(hypercube.submobjects[29])
        hypercube.submobjects[30] = flip_line(hypercube.submobjects[30])
        hypercube.submobjects[31] = flip_line(hypercube.submobjects[31])
        hypercube.set_color(RED)

        # self.add(Dot(ORIGIN).set_color(BLACK).move_to(hypercube.get_center()))
        # counter = Integer(-1).shift(3 * RIGHT)
        # self.add(counter)
        # for edge in hypercube.submobjects:
        #     new_counter = Integer(counter.number + 1).move_to(counter.get_center())
        #     self.bring_to_front(edge)
        #     self.play(
        #         ShowCreation(edge),
        #         ReplacementTransform(counter, new_counter),
        #     )
        #     self.remove(edge)
        #     counter = new_counter
        # self.play(ShowCreation(hypercube))

        anims = [ShowCreation(l) for l in hypercube.submobjects]
        self.play(*anims, run_time=0.3)
        self.wait(0.4)
        self.add(ContinualUpdateFromTimeFunc(
            hypercube,
            rotate_mob,
            start_up_time=0,
        ))
        self.wait(20)


class ClosingScene(Scene):
    def construct(self):
        credits = [
            "Reference Text:",
            "Thomas Cormen",
            "Charles Leiserson",
            "Ronald Rivest",
            "Clifford Stein",
            "Steven Skiena",
            "Music:",
            "Orca Vibes",
            "Zendo",
        ]
        credits = [TextMobject(line) for line in credits]
        for i, credit in enumerate(credits):
            credit.shift(i * DOWN)
            if i >= 6:
                credit.shift(DOWN)

        credits = Group(*credits)
        credits.shift(
            np.array([0, -FRAME_Y_RADIUS - 1, 0]) -
            credits.get_critical_point(UP),
        )

        self.add(ContinualUpdateFromTimeFunc(
            credits,
            lambda c, t: c.shift(t * UP),
        ))
        self.wait(20)
        # self.play(ShowCreation(Group(*credits)))
