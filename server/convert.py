import json
import os
import sys

from os import path
from lib.detector import Detector


params = sys.argv[1]

detector = Detector(params)
output = detector.analyze()

print(json.dumps(output))
