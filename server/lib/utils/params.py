import json


class Params(object):

    def __init__(self, params):
        self._str_params = params
        self._params = json.loads(self._str_params)


    def __getattr__(self, name):
        return self._params[name]


    def __getitem__(self, name):
        return self._params[name]


    def setdefault(self, name, value):
        self._params.setdefault(name, value)
