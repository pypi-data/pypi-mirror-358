from __future__ import annotations

from arcaea_offline_ocr.crop import crop_xywh
from arcaea_offline_ocr.types import Mat, XYWHRect


class ChieriBotV4ComponentRois:
    def __init__(self, factor: float = 1.0):
        self.__factor = factor

    @property
    def factor(self):
        return self.__factor

    @factor.setter
    def factor(self, factor: float):
        self.__factor = factor

    @property
    def top_font_color_detect(self):
        return XYWHRect(35, 10, 120, 100), self.factor

    @property
    def bottom_font_color_detect(self):
        return XYWHRect(30, 125, 175, 110) * self.factor

    @property
    def bg_point(self):
        return (75 * self.factor, 10 * self.factor)

    @property
    def rating_class_rect(self):
        return XYWHRect(21, 40, 7, 20) * self.factor

    @property
    def title_rect(self):
        return XYWHRect(35, 10, 430, 50) * self.factor

    @property
    def jacket_rect(self):
        return XYWHRect(263, 0, 239, 239) * self.factor

    @property
    def score_rect(self):
        return XYWHRect(30, 60, 270, 55) * self.factor

    @property
    def pfl_rect(self):
        return XYWHRect(50, 125, 80, 100) * self.factor

    @property
    def date_rect(self):
        return XYWHRect(205, 200, 225, 25) * self.factor


class ChieriBotV4Rois:
    def __init__(self, factor: float = 1.0):
        self.__factor = factor
        self.__component_rois = ChieriBotV4ComponentRois(factor)

    @property
    def component_rois(self):
        return self.__component_rois

    @property
    def factor(self):
        return self.__factor

    @factor.setter
    def factor(self, factor: float):
        self.__factor = factor
        self.__component_rois.factor = factor

    @property
    def top(self):
        return 823 * self.factor

    @property
    def left(self):
        return 107 * self.factor

    @property
    def width(self):
        return 502 * self.factor

    @property
    def height(self):
        return 240 * self.factor

    @property
    def vertical_gap(self):
        return 74 * self.factor

    @property
    def horizontal_gap(self):
        return 40 * self.factor

    @property
    def horizontal_items(self):
        return 3

    vertical_items = 10

    @property
    def b33_vertical_gap(self):
        return 121 * self.factor

    def components(self, img_bgr: Mat) -> list[Mat]:
        first_rect = XYWHRect(x=self.left, y=self.top, w=self.width, h=self.height)
        results = []

        last_rect = first_rect
        for vi in range(self.vertical_items):
            rect = XYWHRect(*first_rect)
            rect += (0, (self.vertical_gap + self.height) * vi, 0, 0)
            for hi in range(self.horizontal_items):
                if hi > 0:
                    rect += ((self.width + self.horizontal_gap), 0, 0, 0)
                results.append(crop_xywh(img_bgr, rect.rounded()))
            last_rect = rect

        last_rect += (
            -(self.width + self.horizontal_gap) * 2,
            self.height + self.b33_vertical_gap,
            0,
            0,
        )
        for hi in range(self.horizontal_items):
            if hi > 0:
                last_rect += ((self.width + self.horizontal_gap), 0, 0, 0)
            results.append(crop_xywh(img_bgr, last_rect.rounded()))

        return results
