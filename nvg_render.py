from imgui_bundle import nanovg as nvg, hello_imgui
from imgui_bundle import imgui
import numpy as np
from glm import vec2, mat3x3, vec3
import glm
import math
import random

from typing import Literal


class NvgTest:
    def __init__(self, context: nvg.Context) -> None:
        self.context: nvg.Context = context
        self.matrix: mat3x3 = mat3x3()  # Identity matrix
        self.scale: float = 100
        self.dots: list[vec2] = []
        self.mouse: vec2 = vec2()
        self.held: Literal["x", "y", "m"] | None = None
        self.x_unit: vec2 = vec2(1, 0)
        self.y_unit: vec2 = vec2(0, 1)
        self.misc_vector: vec2 = vec2(1, 1)  # Vector in world space

    def draw_line(self, from_point: vec2, to_point: vec2):
        nvg.begin_path(self.context)
        nvg.move_to(self.context, from_point.x, from_point.y)
        nvg.line_to(self.context, to_point.x, to_point.y)
        nvg.stroke(self.context)

    def draw_circle(self, center: vec2, radius: float):
        nvg.begin_path(self.context)
        nvg.circle(self.context, center.x, center.y, radius)
        nvg.fill(self.context)

    def draw_rect_centered(self, center: vec2, size: vec2):
        corner = center - size / 2
        nvg.begin_path(self.context)
        nvg.rect(self.context, corner.x, corner.y, size.x, size.y)
        nvg.fill(self.context)

    def draw_grid(self, spacing: float, lines: int):
        nvg.save(self.context)
        for i in range(-lines, lines):
            nvg.stroke_color(self.context, nvg.rgba(100, 100, 100, 100))
            nvg.begin_path(self.context)
            nvg.move_to(self.context, i * spacing, -1000)
            nvg.line_to(self.context, i * spacing, 1000)
            nvg.stroke(self.context)
            nvg.begin_path(self.context)
            nvg.move_to(self.context, -1000, i * spacing)
            nvg.line_to(self.context, 1000, i * spacing)
            nvg.stroke(self.context)

        nvg.restore(self.context)

    def transform(self, matrix: mat3x3):
        nvg.transform(self.context, matrix[0].x, matrix[0].y, matrix[1].x,
                      matrix[1].y, matrix[2].x, matrix[2].y)

    def get_stroke_width(self) -> float:
        """ 
        This method tries to keep the stroke width consistent.
        Messing with the transforms skews the width of the stroke.
        """
        # 1.414 is an approximation of sqrt 2. Don't ask.
        return 0.1 / max(glm.length(self.matrix[0] + self.matrix[1]), 1.414)

    def point_within_circle(self, point: vec2, circle_center: vec2, radius: float) -> bool:
        difference = point - circle_center
        return glm.length(difference) <= radius

    def render(self, width: float, height: float) -> None:
        nvg.stroke_width(self.context, self.get_stroke_width())

        # Misc vector to show transformation detail.

        # Normal screen positions can be a bit counterintuitive (e.g. +y is down) and hard to look at.
        # Performing a quick transformation to make it more palatable.
        normalizer = mat3x3(self.scale, 0, 0, 0, -self.scale,
                            0, width / 2, height / 2, 1)
        # Performing the visible transformation
        world_transform = normalizer * self.matrix
        self.transform(world_transform)

        self.draw_grid(1, 64)

        # Handle all the mouse interactions
        mouse_global = vec2(
            imgui.get_mouse_pos().x - imgui.get_main_viewport().pos.x,
            imgui.get_mouse_pos().y - imgui.get_main_viewport().pos.y)
        mouse_normalized = glm.inverse(normalizer) * mouse_global
        mouse_local = glm.inverse(world_transform) * mouse_global

        if imgui.is_mouse_released(imgui.MouseButton_.left):
            self.held = None

        if self.held == "x":
            self.matrix[0] = vec3(mouse_normalized.x, mouse_normalized.y, 0)
        elif self.held == "y":
            self.matrix[1] = vec3(mouse_normalized.x, mouse_normalized.y, 0)
        elif self.held == "m":
            self.misc_vector = vec2(mouse_normalized.x, mouse_normalized.y)
        elif imgui.is_mouse_clicked(imgui.MouseButton_.left):
            if self.point_within_circle(mouse_local, self.x_unit, 0.1):
                self.held = "x"
            elif self.point_within_circle(mouse_local, self.y_unit, 0.1):
                self.held = "y"
            elif self.point_within_circle(mouse_local, self.misc_vector, 0.1):
                self.held = "m"

        # Unit Vectors
        nvg.save(self.context)
        nvg.line_cap(self.context, nvg.LineCap.round)
        nvg.stroke_color(self.context, nvg.rgb(255, 0, 0))
        nvg.fill_color(self.context, nvg.rgb(255, 0, 0))
        self.draw_line(vec2(0, 0), self.x_unit)
        nvg.stroke_color(self.context, nvg.rgb(0, 255, 0))
        nvg.fill_color(self.context, nvg.rgb(0, 255, 0))
        self.draw_line(vec2(0, 0), self.y_unit)
        nvg.restore(self.context)

        # Post misc vector
        nvg.stroke_color(self.context, nvg.rgba(255, 255, 0, 100))
        nvg.fill_color(self.context, nvg.rgb(0, 255, 0))
        self.draw_line(vec2(0, 0), self.misc_vector)

        for dot_position in self.dots:
            nvg.fill_color(self.context, nvg.rgb(255, 255, 255))
            self.draw_rect_centered(dot_position, vec2(0.02, 0.02))

        # Resetting the transform for the pre misc vector
        # Seems more stable than transforming by the inverse self matrix.
        nvg.reset_transform(self.context)
        self.transform(normalizer)

        # Showing this vector pre self matrix transform as its the input vector.
        nvg.stroke_color(self.context, nvg.rgb(255, 255, 0))
        nvg.fill_color(self.context, nvg.rgb(0, 255, 0))
        self.draw_line(vec2(0, 0), self.misc_vector)

    def generate_dots(self, amount: int):
        for _ in range(amount):
            self.dots.append(vec2(random.uniform(-1, 1),
                             random.uniform(-1, 1)))

    def clear_dots(self):
        self.dots.clear()

    def reset(self) -> None:
        # The demo that this is copied from had a reset method, it cleaned up images.
        # This is just a placeholder.
        pass
