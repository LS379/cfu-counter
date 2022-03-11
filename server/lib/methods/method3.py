import cv2
import numpy as np

from ..utils import Utils, Output, Params, MethodAccessTrait
from .method1 import Method1


class Method3(Method1, MethodAccessTrait):

    DETAILS = "method 1 + countours on gray"

    def run(self):
        x = int(self._params.x)
        y = int(self._params.y)

        prepare = self.__prepare()
        initial = prepare.copy()
        mask = self.__get_mask(initial, (x, y))
        res = self.__apply_mask(initial, mask)
        gray = self._get_grayscale(res)

        # canny = self._get_edges(initial)
        # blobs = self.__get_blobs(gray)

        circles = self.__get_circles(gray)
        circles = self._convert_circles(circles)

        self._output.circles(circles)
        self.__get_17_gray(initial.copy(), (x, y))


    def __grayscale_17_levels(self, gray):
        high = 255
        while(1):
            low = high - 15
            col_to_be_changed_low = np.array([low])
            col_to_be_changed_high = np.array([high])
            curr_mask = cv2.inRange(gray, col_to_be_changed_low,col_to_be_changed_high)
            gray[curr_mask > 0] = (high)
            high -= 15
            if(low == 0 ):
                break


    @Utils.stage(["17 levels gray", "17 levels rgb"])
    def __get_17_gray(self, image, point):
        mask = object.__getattribute__(self, '_Method1__get_mask')(image, point)

        x, y = point
        height = 50
        width = 50

        crop = self._select(image, x, y, width, height)

        bound_y_start = int(y - height / 2)
        bound_y_stop  = int(y + height / 2)
        bound_x_start = int(x - width / 2)
        bound_x_stop  = int(x + width / 2)

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        self.__grayscale_17_levels(gray)

        rgb = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
        self._show_crop(image, (bound_y_start, bound_x_start), (bound_y_stop, bound_x_stop))

        return gray, rgb, mask
