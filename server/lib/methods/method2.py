import cv2
import numpy as np

from ..utils import Utils, Output, Params, MethodAccessTrait
from .method1 import Method1


class Method2(Method1, MethodAccessTrait):

    DETAILS = "method 1 + contrast enhancement"

    def run(self):
        x = int(self._params.x)
        y = int(self._params.y)

        prepare = self.__prepare()
        initial = prepare.copy()
        mask = self.__get_mask(initial, (x, y))
        res = self.__apply_mask(initial, mask)
        gray = self._get_grayscale(res)
        canny = self._get_edges(initial)
        blobs = self.__get_blobs(gray)
        circles = self.__get_circles(gray)

        circles = self._convert_circles(circles)

        self._output.circles(circles)


    @Utils.stage("prep")
    def __prepare(self):
        img = self._original.copy()

        img[:, :, 0] = cv2.equalizeHist(img[:, :, 0])
        img[:, 0, :] = cv2.equalizeHist(img[:, 0, :])
        img[0, :, :] = cv2.equalizeHist(img[0, :, :])

        initial = self.__contrast(img)

        initial = self.__brightness_and_contrast_adjustment(img)
        initial = self.__averaging_filter(initial)

        initial = self.__brightness_and_contrast_adjustment(initial)
        initial = self.__averaging_filter(initial)

        return initial


    @Utils.stage(["lab", "clahe", "contrast"])
    def __contrast(self, image, channel=cv2.COLOR_BGR2LAB):
        lab = cv2.cvtColor(image, channel)
        l, a, b = cv2.split(lab)

        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        cl = clahe.apply(l)

        limg = cv2.merge((cl,a,b))
        final = cv2.cvtColor(limg, cv2.COLOR_LAB2RGB)

        return lab, cl, final
