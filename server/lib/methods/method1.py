import cv2
import numpy as np

from ..utils import Utils, Output, Params


class Method1(object):

    DETAILS = "general, brightness increased"

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


    @Utils.stage("prep")
    def __prepare(self):
        img = self._original.copy()

        img[:, :, 0] = cv2.equalizeHist(img[:, :, 0])
        img[:, 0, :] = cv2.equalizeHist(img[:, 0, :])
        img[0, :, :] = cv2.equalizeHist(img[0, :, :])

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        initial = self.__brightness_and_contrast_adjustment(img)
        initial = self.__averaging_filter(initial)

        return initial


    @Utils.stage("blobs")
    def __get_blobs(self, image):
        im = image.copy()

        detector = cv2.SimpleBlobDetector_create()
        keypoints = detector.detect(im)

        im_with_keypoints = cv2.drawKeypoints(
            im,
            keypoints,
            np.array([]),
            (0, 255, 0),
            cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS
        )

        return im_with_keypoints, keypoints


    @Utils.stage("median blur")
    def __averaging_filter(self, img):
        smoothed = cv2.medianBlur(img, 15)

        return smoothed


    @Utils.stage("brightness")
    def __brightness_and_contrast_adjustment(self, image, brightness=50, contrast=30):
        img = image.copy()

        img = np.int16(img)
        img = img * (contrast/127+1) - contrast + brightness
        img = np.clip(img, 0, 255)
        img = np.uint8(img)

        return img


    def __iterate_get_lower_upper(self, img, x, y, width=None, height=None, threshold=7):
        img = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)

        crop = self._select(img, x, y, width=width, height=height)
        dominant = self.__get_dominant_color(crop)

        self._output.values.append(dominant.tolist())

        abc = dominant
        a, b, c = abc

        minABC = np.array([a - threshold, b - threshold, c - threshold])
        maxABC = np.array([a + threshold, b + threshold, c + threshold])

        return minABC, maxABC


    def __get_dominant_color(self, crop):
        crop = crop.copy()

        average = crop.mean(axis=0).mean(axis=0)
        pixels = np.float32(crop.reshape(-1, 3))

        n_colors = 1
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, .1)
        flags = cv2.KMEANS_RANDOM_CENTERS

        _, labels, palette = cv2.kmeans(pixels, n_colors, None, criteria, 10, flags)
        _, counts = np.unique(labels, return_counts=True)

        dominant = palette[np.argmax(counts)]

        return dominant


    @Utils.stage("mask")
    def __get_mask(self, img, point, steps=5, growth=4, offset=2):
        mask = None
        initial_hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
        lower_array = []
        upper_array = []

        x, y = point

        for i in range(steps):
            square_side = i * growth + offset
            lower, upper = self.__iterate_get_lower_upper(img, x, y, square_side, square_side)

            if mask is None:
                mask = self.__filter_range(initial_hsv, lower, upper)
            else:
                mask = mask | self.__filter_range(initial_hsv, lower, upper)

        mask = mask | self.__filter_range(initial_hsv, np.mean(lower_array), np.mean(upper_array))

        return mask


    def __filter_range(self, img, lower, upper):
        img = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)

        mask = cv2.inRange(img, lower, upper)
        return mask


    @Utils.stage("res")
    def __apply_mask(self, img, mask):
        res = cv2.bitwise_and(img, img, mask=mask)
        return res


    def __get_circles(self, img, params=None):
        default_params = {
            "image": img,
            "method": cv2.HOUGH_GRADIENT,
            "dp": 1,
            "minDist": 50,
            "param1": 70,
            "param2": 15,
            "minRadius": 3,
            "maxRadius": 100
        }

        params = params if isinstance(params, dict) else {}
        default_params.update(params)

        circles = cv2.HoughCircles(**default_params)
        self._draw_circles(img, circles)

        return circles
