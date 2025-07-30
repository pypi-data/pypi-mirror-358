# Copyright (C) Siemens AG 2021. All Rights Reserved. Confidential.

import os
import re
import sys
import csv
import logging
from pathlib import Path
from simaticai.testing.data_stream import DataStream
from typing import Optional

logging.basicConfig()
logging.getLogger().handlers = [logging.StreamHandler(sys.stdout)]
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)

class TimeSeriesStream(DataStream):
    """
    This class creates a generator from a csv file.

    The generate function returns a generator that reads the csv file line by line and
    converts each line to an input dictionary, as if it were received from AI Inference Server.
    """

    def __init__(self, csv_path: os.PathLike, *, fields: Optional[list] = None, count: Optional[int] = None, offset: Optional[int] = None, batch_size: Optional[int] = None):
        """
        Creates a new TimeSeriesStream object

        Args:
            data (os.Pathlike): Path to the csv file
        """
        self.csv_path = Path(csv_path)
        if fields is None:
            self.fields = []
        else:
            self.fields = fields

        with open(self.csv_path, "r") as file:
            self.header = file.readline().strip().split(",")

        if any(key for key in self.fields if key not in self.header):
            raise KeyError("The CSV file must contain variable names in the first row.")

        if self.fields == []:
            self.fields = self.header
            fields_len = len(self.fields)
            filtered_len = len(list(k for k in self.fields if re.match("[a-zA-Z]+", k)))
            if filtered_len != fields_len:
                raise KeyError("Column headers should start with a letter.")

        if (not isinstance(count, int)) or count < 0:
            self.count = 0
        else:
            self.count = count
        if (not isinstance(offset, int)) or offset < 0:
            self.offset = 0
        else:
            self.offset = offset
        if (not isinstance(batch_size, int)) or batch_size < 0:
            self.batch_size = 0
        else:
            self.batch_size = batch_size

    def _read_value(self, value):
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return value

    def _read_csv(self):
        with open(self.csv_path, 'r', encoding='UTF-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for line in csv_reader:
                if 0 < len(self.fields):
                    key_holder = self.fields
                else:
                    key_holder = line.keys()
                result = {}
                for k in key_holder:
                    result[k] = self._read_value(line[k])
                yield result

    def _limit(self):
        _max = float('inf')
        if 0 < self.count:
            _max = self.offset + self.count
        counter = 0
        for line in self._read_csv():
            if _max <= counter:
                break
            counter += 1
            if counter <= self.offset:
                continue
            yield line

    def _batch(self):
        aggregate = []
        for line in self._limit():
            if len(aggregate) < self.batch_size:
                aggregate += [line]
                continue
            yield aggregate
            aggregate = [line]
        if self.batch_size == len(aggregate):
            yield aggregate
        else:
            _logger.warning(f"WARNING! The length of the given dataset is not divisible by {self.batch_size}. There are {len(aggregate)} inputs remaining in the buffer.")

    def __iter__(self):
        """
        Creates the input data generator.

        Returns: a generator
        """
        if 0 < self.batch_size:
            return self._batch()
        else:
            return self._limit()
