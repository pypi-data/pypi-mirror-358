# Copyright (C) Siemens AG 2021. All Rights Reserved. Confidential.

class DataStream:
    """
    Base class for datastream generators
    """

    def __iter__(self):
        """
        Empty generator method for child classess to implement.
        """
        raise NotImplementedError('Child classes must implement this method.')
