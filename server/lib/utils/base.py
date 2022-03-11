import os, sys
import cv2
import base64
import importlib



class Utils(object):

    @staticmethod
    def tobase64(img):
        image = img.copy()
        _, buffer = cv2.imencode('.jpg', image)
        jpg_as_text = base64.b64encode(buffer)

        return "data:image/png;base64,{}".format(jpg_as_text)


    @staticmethod
    def stage(name):
        def decorator(func):
            def wrapper(self, *args, **kwargs):
                return_img = func(self, *args, **kwargs)
                if return_img is None:
                    return

                if isinstance(return_img, tuple):
                    if not isinstance(name, list):
                        names = [name]
                    else:
                        names = name

                    return_imgs = [item for item in return_img]

                    for i, image in enumerate(return_imgs):
                        if i < len(names):
                            self._output.stage(names[i], return_imgs[i])
                        else:
                            return return_imgs[i:]

                    return return_imgs[-1]
                else:
                    self._output.stage(name, return_img)

                return return_img
            return wrapper
        return decorator


    @staticmethod
    def path(file):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../data', file)
        return path


    @staticmethod
    def extend_object(obj, base):
        cls = obj.__class__
        obj.__class__ = cls.__class__(base.__name__, (cls, base), {})


    @staticmethod
    def get_method(method):
        sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/..')
        sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '../..')

        module = '..methods.method{}'.format(method)
        name = "Method{}".format(method)

        method_class = Utils.import_class(module, name)
        return method_class


    @staticmethod
    def import_class(module, name):
        exec('from {} import {}'.format(module, name))
        kls = locals()[name]

        if not kls:
            raise ValueError("{} not found".format(name))

        return kls
