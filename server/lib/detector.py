import cv2
import numpy as np
import math

from collections import OrderedDict

from .utils import Utils, Output, Params, DEFAULTS



class Detector(object):

    def __init__(self, params):
        self._params = Params(params)
        self._original = None
        self._output = Output()

        self._params.setdefault('method', DEFAULTS['method'])

        self._add_method(self._params['method'])
        self._read(self._params.file)


    def analyze(self):
        self.run()
        return self._output.dump()


    def _add_method(self, method):
        method = Utils.get_method(method)
        Utils.extend_object(self, method)


    def _read(self, file):
        path = Utils.path(file)

        self._original = cv2.imread(path)
        self._original = cv2.cvtColor(self._original, cv2.COLOR_BGR2RGB)


    @Utils.stage("gray")
    def _get_grayscale(self, image, channel=cv2.COLOR_RGB2GRAY):
        gray = cv2.cvtColor(image, channel)

        return gray


    @Utils.stage("crop")
    def _show_crop(self, image, point_start, point_stop):
        bound_y_start, bound_x_start = point_start
        bound_y_stop, bound_x_stop = point_stop

        height = image.shape[0]
        width = image.shape[1]
        mask = np.zeros((height, width))
        points = np.array([
            [
                [bound_x_start, bound_y_start],
                [bound_x_stop, bound_y_start],
                [bound_x_stop, bound_y_stop],
                [bound_x_start, bound_y_stop]
            ]
        ])
        cv2.fillPoly(mask, points, (255))

        mask = mask.astype('int8')
        res = cv2.bitwise_and(image, image, mask=mask)

        return res


    def _select(self, image, x, y, width=50, height=50, channel=cv2.COLOR_RGB2HSV):
        image = image.copy()

        bound_y_start = int(y - height/2)
        bound_y_stop = int(y + height/2)
        bound_x_start = int(x - width/2)
        bound_x_stop = int(x + width/2)

        image_crop = image[
            bound_y_start: bound_y_stop,
            bound_x_start: bound_x_stop
        ].copy()

        hsv_mat = cv2.cvtColor(image_crop, channel)
        self._show_crop(image, (bound_y_start, bound_x_start), (bound_y_stop, bound_x_stop))

        return hsv_mat


    @Utils.stage("canny")
    def _get_edges(self, img, ):
        canny_edge = cv2.Canny(img, 1, 60)
        return canny_edge


    def _filter_range(self, image, lower, upper, channel=cv2.COLOR_RGB2HSV):
        image = cv2.cvtColor(image, channel)
        mask = cv2.inRange(image, lower, upper)

        return mask


    @Utils.stage("circles")
    def _draw_circles(self, image, circles, channel=cv2.COLOR_GRAY2RGB):
        if circles is None:
            return

        output = cv2.cvtColor(image, channel)
        circles1 = np.round(circles[0, :]).astype("int")

        for (x, y, r) in circles1:
            cv2.circle(output, (x, y), r, (0, 255, 0), 4)
            cv2.rectangle(output, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)

        return output


    def _convert_circles(self, circles):
        if circles is not None:
            circles = np.uint16(np.around(circles)).tolist()
        else:
            circles = []

        return circles
