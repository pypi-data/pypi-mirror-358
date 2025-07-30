# Copyright (C) Siemens AG 2021. All Rights Reserved. Confidential.

import os
import datetime
import cv2
import numpy as np
import uuid
from pathlib import Path
from simaticai.testing.data_stream import DataStream

_supported_image_formats = ['BayerRG8', 'BGR']

class VCAStream(DataStream):
    """
    This class creates a generator from a folder of images.

    The generate function returns a generator that walks over the image folder and converts
    each image into the specified format, BayerRG8 by default. The resulting object is in the
    ImageSet format, as if it were received from AI Inference Server.
    """

    def __init__(self, data: os.PathLike, variable_name: str = 'vision_payload', image_format: str = 'BayerRG8', filter = None):
        """
        Creates a new VCAStream object

        Args:
            data (os.Pathlike): Path to the directory of images
            variable_name (str): Name of the variable to store the images (default: 'vision_payload')
            image_format (str): Supported image formats: 'BayerRG8' or 'BGR'
            filter (rglob_pattern): Pattern to filter the images (see also: pathlib.rglob())
        """
        self.seq = 0
        self.data = data
        if filter is None or "" == filter.strip():
            self.filter = "**/*.[jJpP][pPnN][gGeE]*"
        else:
            self.filter = filter
        if variable_name is None or "" == variable_name.strip():
            self.variable_name = 'vision_payload'
        else:
            self.variable_name = variable_name
        if image_format not in _supported_image_formats:
            raise AssertionError(f'ERROR Provided image format is not supported. image_format must be one of {_supported_image_formats}')
        self.image_format = image_format
        self.camera_id = uuid.uuid4()

    def __iter__(self):
        """
        Creates the input data generator.

        Walks recursively the image folder and converts each image into an ImageSet variable.

        Returns: a generator
        """
        for image_path in Path(self.data).rglob(self.filter):
            yield self._create_imageset(image_path)

    def _to_BGR(self, image_path):
        im = cv2.imread(str(image_path))
        (height, width) = im.shape[:2]
        return im, width, height

    def _to_bayerRG8(self, image_path):
        im = cv2.imread(str(image_path))
        (height, width) = im.shape[:2]
        (R,G,B) = cv2.split(im)

        bayerrg8 = np.zeros((height, width), np.uint8)
        bayerrg8[0::2, 0::2] = R[0::2, 1::2]  # top left
        bayerrg8[0::2, 1::2] = G[0::2, 0::2]  # top right
        bayerrg8[1::2, 0::2] = G[1::2, 1::2]  # bottom left
        bayerrg8[1::2, 1::2] = B[1::2, 0::2]  # bottom right
        bayerrg8 = bayerrg8.ravel().tobytes()

        return bayerrg8, width, height

    def _create_imageset(self, image_path):
        timestamp = f"{datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]}Z"
        if 'BayerRG8' == self.image_format:
            image_array, width, height = self._to_bayerRG8(image_path)
        else:  # default to BGR
            image_array, width, height = self._to_BGR(image_path)
        result = {
            self.variable_name: {
                'version': '1',
                'cameraid': str(self.camera_id),
                'timestamp': timestamp,
                'customfields': '',
                'detail': [{
                    'id': f'VCA Stream : {image_path}',
                    'seq': self.seq,
                    'timestamp': timestamp,
                    'format': self.image_format,
                    'width': width,
                    'height': height,
                    'metadata': '{"ptpstatus":"Disabled","ptptimestamp":"0"}',
                    'image': image_array,
                }]}
        }
        self.seq += 1
        return result
