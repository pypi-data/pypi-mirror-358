from tfcat.base import Base
from astropy.units import Unit, Quantity


class Field(Base):
    """Class for TFCat Field Object

    The Field object is used to ddefine the metadtat

    :param info: description information for the field
    :type info: str
    :param datatype: data type of the field (str, float, int)
    :type datatype: str
    :param ucd: UCD of the field
    :type ucd: str
    :param unit: Unit of the field (optional for ``str`` datatype)
    :type unit: str
    """
    def __init__(self, info=None, datatype=None, ucd=None, unit=None, **extra):
        super(Field).__init__(**extra)
        self.info = info
        self.datatype = datatype
        self.ucd = ucd
        self.unit = unit
