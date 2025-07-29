# -*- coding: utf-8 -*-


class PstParam(object):

    """Implementation of the 'PstParam' model.

    Specifies the PST conversion specific parameters.

    Attributes:
        create_pst (bool): Specifies if create a PST or MSG for input items.
        password (string): Specifies Password to be set for generated PSTs.
        size_threshold_bytes (long|int): Specifies PST size threshold in bytes.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "create_pst":'createPst',
        "password":'password',
        "size_threshold_bytes":'sizeThresholdBytes'
    }

    def __init__(self,
                 create_pst=None,
                 password=None,
                 size_threshold_bytes=None):
        """Constructor for the PstParam class"""

        # Initialize members of the class
        self.create_pst = create_pst
        self.password = password
        self.size_threshold_bytes = size_threshold_bytes


    @classmethod
    def from_dictionary(cls,
                        dictionary):
        """Creates an instance of this model from a dictionary

        Args:
            dictionary (dictionary): A dictionary representation of the object as
            obtained from the deserialization of the server's response. The keys
            MUST match property names in the API description.

        Returns:
            object: An instance of this structure class.

        """
        if dictionary is None:
            return None

        # Extract variables from the dictionary
        create_pst = dictionary.get('createPst')
        password = dictionary.get('password')
        size_threshold_bytes = dictionary.get('sizeThresholdBytes')

        # Return an object of this model
        return cls(create_pst,
                   password,
                   size_threshold_bytes)