class PyCCEError(Exception):
    """Base class for all custom exceptions in the PyCCE package.

    This class should be used as the parent for any custom error specific to the functionality
    of the PyCCE estimators, preprocessing, or utility modules.
    """

    pass


class PanelDataError(PyCCEError):
    """Exception raised for errors related to transforming input data to panel data.

    This includes issues such as invalid shapes, unsupported data types, or improper indexing
    (e.g., missing MultiIndex in a pandas DataFrame).
    """

    pass
