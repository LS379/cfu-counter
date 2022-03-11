import cv2
import base64
import numpy as np
import math

from collections import OrderedDict


class Detector(object):


    def __init__(self):
        self._original = None
        self._images = {}
        self._output = OrderedDict({})
        self._output['stages'] = OrderedDict({})


    @staticmethod
    def tobase64(img):
        image = img.copy()
        _, buffer = cv2.imencode('.jpg', image)
        jpg_as_text = base64.b64encode(buffer)

        return "data:image/png;base64,{}".format(jpg_as_text)


    def run(self, params):
        x = params['x']
        y = params['y']

        original = self.prepare()
        initial = original.copy()

        steps = 15

        mask = None
        initial_hsv = cv2.cvtColor(initial, cv2.COLOR_RGB2HSV)
        lower_array = []
        upper_array = []

        for i in range(steps):
            square_side = i * 4 + 2
            lower, upper = self._iterate_get_lower_upper(initial, x, y, square_side, square_side)

            if mask is None:
                mask = self.get_mask(initial_hsv, lower, upper)
            else:
                mask = mask | self.get_mask(initial_hsv, lower, upper)
            
            # self._output['stages']['mask {}'.format(square_side)] = self.tobase64(mask)

        mask = mask | self.get_mask(initial_hsv, np.mean(lower_array), np.mean(upper_array))

        res = self.apply_mask(initial_hsv, mask)
        gray = cv2.cvtColor(res, cv2.COLOR_RGB2GRAY)

        self._output['stages']['prep'] = self.tobase64(original)
        self._output['stages']['hsv'] = self.tobase64(initial_hsv)
        self._output['stages']['mask'] = self.tobase64(mask)
        self._output['stages']['res'] = self.tobase64(res)
        self._output['stages']['gray'] = self.tobase64(gray)

        canny = self._get_edges(initial)

        circles = self.get_circles(gray)
        blobs = self._get_blobs(gray)

        final = circles

        if circles is not None:
            circles = np.uint16(np.around(final)).tolist()
        else:
            circles = []

        self._output['circles'] = circles
        return self._output


    def read(self, path):
        self._original = cv2.imread(path)
        self._original = cv2.cvtColor(self._original, cv2.COLOR_BGR2RGB)


    def prepare(self, image=None):
        image = image if image is not None else self._original
        img = image.copy()

        img = cv2.medianBlur(img, 9)
        img[:,:,0] = cv2.equalizeHist(img[:,:,0])
        img[:,0,:] = cv2.equalizeHist(img[:,0,:])
        img[0,:,:] = cv2.equalizeHist(img[0,:,:])

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self._images['prepare'] = img

        initial = self._brightness_and_contrast_adjustment(img)
        initial = self._averaging_filter(initial)

        initial = self._brightness_and_contrast_adjustment(initial)
        initial = self._averaging_filter(initial)

        self._images['initial'] = initial
        return initial


    def _get_blobs(self, image):
        im = image.copy()

        detector = cv2.SimpleBlobDetector_create()
        keypoints = detector.detect(im)
        
        im_with_keypoints = cv2.drawKeypoints(
            im,
            keypoints,
            np.array([]),
            (0,255,0),
            cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS
        )

        self._output['stages']['blob'] = self.tobase64(im_with_keypoints)
        return keypoints


    def _averaging_filter(self, img):
        smoothed = cv2.medianBlur(img, 15)

        self._output['stages']['smoothed'] = self.tobase64(smoothed)
        return smoothed


    def _brightness_and_contrast_adjustment(self, image, brightness=50, contrast=30):
        img = image.copy()

        img = np.int16(img)
        img = img * (contrast/127+1) - contrast + brightness
        img = np.clip(img, 0, 255)
        img = np.uint8(img)

        self._output['stages']['adjustements'] = self.tobase64(img)
        return img


    def _get_crop(self, img, x, y, width=50, height=50):
        image_orig = img.copy()

        bound_y_start = int(y - height/2)
        bound_y_stop = int(y + height/2)
        bound_x_start = int(x - width/2)
        bound_x_stop = int(x + width/2)

        image_crop = image_orig[
            bound_y_start: bound_y_stop,
            bound_x_start: bound_x_stop
        ].copy()

        # blurred = cv2.GaussianBlur(image_crop, (5, 5), 0)
        hsv_mat = cv2.cvtColor(image_crop, cv2.COLOR_RGB2HSV);

        height = image_orig.shape[0]
        width = image_orig.shape[1]
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
        res = cv2.bitwise_and(image_orig, image_orig, mask=mask)
        self._output['stages']['crop'] = self.tobase64(res)

        # hsv_res = cv2.cvtColor(res, cv2.COLOR_RGB2HSV)
        # self._output['stages']['hsv crop'] = self.tobase64(hsv_res)

        return hsv_mat


    def _get_edges(self, img):
        canny_edge = cv2.Canny(img, 1, 60)

        self._output['stages']['edges'] = self.tobase64(canny_edge)

        return canny_edge


    def _iterate_get_lower_upper(self, img, x, y, width=None, height=None):
        img = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)

        crop = self._get_crop(img, x, y, width=width, height=height)
        dominant = self._get_dominant_color(crop)

        self._output.setdefault('values', [])
        self._output['values'].append(dominant.tolist())

        abc = dominant
        a, b, c = abc
        thresh = 2

        minABC = np.array([a - thresh, b - thresh, c - thresh])
        maxABC = np.array([a + thresh, b + thresh, c + thresh])

        return minABC, maxABC


    def get_lower_upper(self, img, x, y, width=None, height=None):
        img = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
        abc = img[y][x]

        a, b, c = abc
        thresh = 7
        
        minABC = np.array([a - thresh, b - thresh, c - thresh])
        maxABC = np.array([a + thresh, b + thresh, c + thresh])

        return minABC, maxABC


    def _get_dominant_color(self, crop):
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



    def get_mask(self, img, lower, upper):
        img = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)

        mask = cv2.inRange(img, lower, upper)
        return mask


    def apply_mask(self, img, mask):
        res = cv2.bitwise_and(img, img, mask=mask)
        return res


    def get_circles(self, img, params=None):
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

        if circles is not None:
            output = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    	    circles1 = np.round(circles[0, :]).astype("int")

            for (x, y, r) in circles1:
                cv2.circle(output, (x, y), r, (0, 255, 0), 4)
                cv2.rectangle(output, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)

            self._output['stages']['circles'] = self.tobase64(output)
    
        return circles
