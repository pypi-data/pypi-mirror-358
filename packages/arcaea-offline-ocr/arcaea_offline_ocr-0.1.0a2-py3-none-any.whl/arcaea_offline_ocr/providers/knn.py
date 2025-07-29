from __future__ import annotations

import logging
import math
from typing import TYPE_CHECKING, Callable, Sequence

import cv2
import numpy as np

from arcaea_offline_ocr.crop import crop_xywh

from .base import OcrTextProvider

if TYPE_CHECKING:
    from cv2.ml import KNearest

    from arcaea_offline_ocr.types import Mat

logger = logging.getLogger(__name__)


class FixRects:
    @staticmethod
    def connect_broken(
        rects: Sequence[tuple[int, int, int, int]],
        img_width: int,
        img_height: int,
        tolerance: int | None = None,
    ):
        # for a "broken" digit, please refer to
        # /assets/fix_rects/broken_masked.jpg
        # the larger "5" in the image is a "broken" digit

        if tolerance is None:
            tolerance = math.ceil(img_width * 0.08)

        new_rects = []
        consumed_rects = []
        for rect in rects:
            if rect in consumed_rects:
                continue

            x, _, w, h = rect
            # grab those small rects
            if not img_height * 0.1 <= h <= img_height * 0.6:
                continue

            group = []
            # see if there's other rects that have near left & right borders
            for other_rect in rects:
                if rect == other_rect:
                    continue
                ox, _, ow, _ = other_rect
                if abs(x - ox) < tolerance and abs((x + w) - (ox + ow)) < tolerance:
                    group.append(other_rect)

            if group:
                group.append(rect)
                consumed_rects.extend(group)
                # calculate the new rect
                new_x = min(r[0] for r in group)
                new_y = min(r[1] for r in group)
                new_right = max(r[0] + r[2] for r in group)
                new_bottom = max(r[1] + r[3] for r in group)
                new_w = new_right - new_x
                new_h = new_bottom - new_y
                new_rects.append((new_x, new_y, new_w, new_h))

        return_rects = [r for r in rects if r not in consumed_rects]
        return_rects.extend(new_rects)
        return return_rects

    @staticmethod
    def split_connected(
        img_masked: Mat,
        rects: Sequence[tuple[int, int, int, int]],
        rect_wh_ratio: float = 1.05,
        width_range_ratio: float = 0.1,
    ):
        connected_rects = []
        new_rects = []
        for rect in rects:
            rx, ry, rw, rh = rect
            if rw / rh <= rect_wh_ratio:
                continue

            connected_rects.append(rect)

            # find the thinnest part
            border_ignore = round(rw * width_range_ratio)
            img_cropped = crop_xywh(
                img_masked,
                (border_ignore, ry, rw - border_ignore, rh),
            )
            white_pixels = {}  # dict[x, white_pixel_number]
            for i in range(img_cropped.shape[1]):
                col = img_cropped[:, i]
                white_pixels[rx + border_ignore + i] = np.count_nonzero(col > 200)

            if all(v == 0 for v in white_pixels.values()):
                return rects

            least_white_pixels = min(v for v in white_pixels.values() if v > 0)
            x_values = [
                x for x, pixel in white_pixels.items() if pixel == least_white_pixels
            ]
            # select only middle values
            x_mean = np.mean(x_values)
            x_std = np.std(x_values)
            x_values = [
                x for x in x_values if x_mean - x_std * 1.5 <= x <= x_mean + x_std * 1.5
            ]
            x_mid = round(np.median(x_values))

            # split the rect
            new_rects.extend(
                [(rx, ry, x_mid - rx, rh), (x_mid, ry, rx + rw - x_mid, rh)],
            )

        return_rects = [r for r in rects if r not in connected_rects]
        return_rects.extend(new_rects)
        return return_rects


def resize_fill_square(img: Mat, target: int = 20):
    h, w = img.shape[:2]
    if h > w:
        new_h = target
        new_w = round(w * (target / h))
    else:
        new_w = target
        new_h = round(h * (target / w))
    resized = cv2.resize(img, (new_w, new_h))

    border_size = math.ceil((max(new_w, new_h) - min(new_w, new_h)) / 2)
    if new_w < new_h:
        resized = cv2.copyMakeBorder(
            resized,
            0,
            0,
            border_size,
            border_size,
            cv2.BORDER_CONSTANT,
        )
    else:
        resized = cv2.copyMakeBorder(
            resized,
            border_size,
            border_size,
            0,
            0,
            cv2.BORDER_CONSTANT,
        )
    return cv2.resize(resized, (target, target))


def preprocess_hog(digit_rois):
    # https://learnopencv.com/handwritten-digits-classification-an-opencv-c-python-tutorial/
    samples = []
    for digit in digit_rois:
        hog = cv2.HOGDescriptor((20, 20), (10, 10), (5, 5), (10, 10), 9)
        hist = hog.compute(digit)
        samples.append(hist)
    return np.float32(samples)


def ocr_digit_samples_knn(samples, knn_model: cv2.ml.KNearest, k: int = 4):
    _, results, _, _ = knn_model.findNearest(samples, k)
    return [int(r) for r in results.ravel()]


class OcrKNearestTextProvider(OcrTextProvider):
    _ContourFilter = Callable[["Mat"], bool]
    _RectsFilter = Callable[[Sequence[int]], bool]

    def __init__(self, model: KNearest):
        self.model = model

    def contours(
        self,
        img: Mat,
        /,
        *,
        contours_filter: _ContourFilter | None = None,
    ):
        cnts, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        if contours_filter:
            cnts = list(filter(contours_filter, cnts))

        return cnts

    def result_raw(
        self,
        img: Mat,
        /,
        *,
        fix_rects: bool = True,
        contours_filter: _ContourFilter | None = None,
        rects_filter: _RectsFilter | None = None,
    ):
        """
        :param img: grayscaled roi
        """

        try:
            cnts, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours_filter:
                cnts = list(filter(contours_filter, cnts))

            rects = [cv2.boundingRect(cnt) for cnt in cnts]
            if fix_rects and rects_filter:
                rects = FixRects.connect_broken(rects, img.shape[1], img.shape[0])
                rects = list(filter(rects_filter, rects))
                rects = FixRects.split_connected(img, rects)
            elif fix_rects:
                rects = FixRects.connect_broken(rects, img.shape[1], img.shape[0])
                rects = FixRects.split_connected(img, rects)
            elif rects_filter:
                rects = list(filter(rects_filter, rects))

            rects = sorted(rects, key=lambda r: r[0])

            digits = []
            for rect in rects:
                digit = crop_xywh(img, rect)
                digit = resize_fill_square(digit, 20)
                digits.append(digit)
            samples = preprocess_hog(digits)
            return ocr_digit_samples_knn(samples, self.model)
        except Exception:
            logger.exception("Error occurred during KNearest OCR")
            return None

    def result(
        self,
        img: Mat,
        /,
        *,
        fix_rects: bool = True,
        contours_filter: _ContourFilter | None = None,
        rects_filter: _RectsFilter | None = None,
    ):
        """
        :param img: grayscaled roi
        """

        raw = self.result_raw(
            img,
            fix_rects=fix_rects,
            contours_filter=contours_filter,
            rects_filter=rects_filter,
        )
        return (
            "".join(["".join(str(r) for r in raw if r > -1)])
            if raw is not None
            else None
        )
