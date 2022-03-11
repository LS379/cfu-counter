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
        retval, buffer = cv2.imencode('.jpg', image)
        jpg_as_text = base64.b64encode(buffer)

        return "data:image/png;base64,{}".format(jpg_as_text)


    def run(self, params):
        x = params['x']
        y = params['y']

        initial = self.prepare()
        lower, upper = self.get_lower_upper(initial, x, y)
        mask = self.get_mask(initial, lower, upper)
        res = self.apply_mask(initial, mask)
        gray = cv2.cvtColor(res, cv2.COLOR_RGB2GRAY)

        self._output['stages']['prep'] = self.tobase64(initial)
        self._output['stages']['mask'] = self.tobase64(mask)
        self._output['stages']['res'] = self.tobase64(res)
        self._output['stages']['gray'] = self.tobase64(gray)

        # canny = self._get_edges(initial)

        circles = self.get_circles(gray)
        blobs = self._get_blobs(gray)
        other_circles = self._get_other_circles(res)

        # final = blobs + circles + other_circles
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
        img = image if image is not None else self._original
        img = img.copy()

        img = cv2.medianBlur(img, 9)
        img[:,:,0] = cv2.equalizeHist(img[:,:,0])
        img[:,0,:] = cv2.equalizeHist(img[:,0,:])
        img[0,:,:] = cv2.equalizeHist(img[0,:,:])

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        self._images['prepare'] = img
        return img


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

        blurred = cv2.GaussianBlur(image_crop, (5, 5), 0)
        hsv_mat = cv2.cvtColor(blurred, cv2.COLOR_RGB2HSV);

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
        hsv_res = cv2.cvtColor(res, cv2.COLOR_RGB2HSV)

        self._output['stages']['rgb crop'] = self.tobase64(res)
        self._output['stages']['hsv crop'] = self.tobase64(hsv_res)

        return hsv_mat


    def _get_edges(self, img):
        canny_edge = cv2.Canny(img, 1, 60)

        self._output['stages']['canny'] = self.tobase64(canny_edge)

        return canny_edge


    def _get_other_circles(self, image):
        d_red = np.array([150, 55, 65])
        l_red = np.array([250, 200, 200])

        orig = image.copy()
        img = orig.copy()
        img2 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        detector = cv2.MSER_create()
        fs = detector.detect(img2)
        fs.sort(key = lambda x: -x.size)

        def supress(x):
            for f in fs:
                distx = f.pt[0] - x.pt[0]
                disty = f.pt[1] - x.pt[1]
                dist = math.sqrt(distx*distx + disty*disty)
                if (f.size > x.size) and (dist<f.size/2):
                    return True

        sfs = [x for x in fs if not supress(x)]

        for f in sfs:
            cv2.circle(img, (int(f.pt[0]), int(f.pt[1])), int(f.size/2), d_red, 2, cv2.LINE_AA)
            cv2.circle(img, (int(f.pt[0]), int(f.pt[1])), int(f.size/2), l_red, 1, cv2.LINE_AA)

        h, w = orig.shape[:2]
        vis = np.zeros((h, w*2+5), np.uint8)
        vis = cv2.cvtColor(vis, cv2.COLOR_GRAY2BGR)

        self._output['stages']['circles'] = self.tobase64(img)

        return sfs 


    def get_lower_upper(self, img, x, y):
        crop = self._get_crop(img, x, y)

        bgr = img[y][x]
        thresh = 10

        minBGR = np.array([bgr[0] - thresh, bgr[1] - thresh, bgr[2] - thresh])
        maxBGR = np.array([bgr[0] + thresh, bgr[1] + thresh, bgr[2] + thresh])

        return minBGR, maxBGR


    def get_mask(self, img, lower, upper):
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
            "minDist": 13,
            "param1": 70,
            "param2": 20,
            "minRadius": 5,
            "maxRadius": 100
        }

        params = params if isinstance(params, dict) else {}
        default_params.update(params)

        circles = cv2.HoughCircles(**default_params)
    
        return circles
