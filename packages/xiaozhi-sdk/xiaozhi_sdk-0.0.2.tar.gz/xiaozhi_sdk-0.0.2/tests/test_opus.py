import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from xiaozhi_sdk.utils import setup_opus

setup_opus()
import opuslib
