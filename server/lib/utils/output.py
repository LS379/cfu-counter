from collections import OrderedDict

from .base import Utils


class Output(object):

    def __init__(self):
        self._output = OrderedDict({})
        self._output["stages"] = OrderedDict({})
        self._output["circles"] = []
        self._output["values"] = []

        self._stages = self._output["stages"]
        self._circles = self._output["circles"]
        self._values = self._output["values"]


    def stage(self, name, value):
        self._stages[name] = Utils.tobase64(value)


    def circles(self, circles):
        self._output["circles"] = circles


    @property
    def values(self):
        return self._values


    def dump(self):
        return self._output
