import tfcat.codec
import tfcat.factory


class Base(dict):
    """
    A class representing a TFCat base object.
    """

    def __init__(self, iterable=(), **extra):
        """
        Initialises a TFCat base object

        :param iterable: iterable from which to draw the content of the TFCat object.
        :type iterable: dict, array, tuple
        :return: a TFCat (Base or inherited from Base) object
        :rtype: Base
        """
        super(Base, self).__init__(iterable)
        self["type"] = getattr(self, "type", type(self).__name__)
        self.update(extra)

    def __repr__(self):
        return tfcat.codec.dumps(self, sort_keys=True)

    __str__ = __repr__

    def __getattr__(self, name):
        """
        Permit dictionary items to be retrieved like object attributes

        :param name: attribute name
        :type name: str, int
        :return: dictionary value
        """
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        """
        Permit dictionary items to be set like object attributes.

        :param name: key of item to be set
        :type name: str
        :param value: value to set item to
        """

        self[name] = value

    def __delattr__(self, name):
        """
        Permit dictionary items to be deleted like object attributes

        :param name: key of item to be deleted
        :type name: str
        """

        del self[name]

    @classmethod
    def to_instance(cls, ob, default=None, strict=False):
        """Encode a Base dict into a Base object.
        Assumes the caller knows that the dict should satisfy a TFCat type.

        :param cls: Dict containing the elements to be encoded into a TFCat
        object.
        :type cls: dict
        :param ob: TFCat object into which to encode the dict provided in
        `cls`.
        :type ob: Base
        :param default: A default instance to append the content of the dict
        to if none is provided.
        :type default: Base
        :param strict: Raise error if unable to coerce particular keys or
        attributes to a valid TFCat structure.
        :type strict: bool
        :return: A TFCat object with the dict's elements as its constituents.
        :rtype: Base
        :raises TypeError: If the input dict contains items that are not valid
        TFCat types.
        :raises UnicodeEncodeError: If the input dict contains items of a type
        that contain non-ASCII characters.
        :raises AttributeError: If the input dict contains items that are not
        valid TFCat types.
        """
        if ob is None and default is not None:
            instance = default()
        elif isinstance(ob, Base):
            instance = ob
        else:
            mapping = ob
            d = {}
            for k in mapping:
                d[k] = mapping[k]
            try:
                type_ = d.pop("type")
                try:
                    type_ = (type_.encode('ascii') if isinstance(type_, str) else type_).decode('ascii')
                except UnicodeEncodeError:
                    # If the type contains non-ascii characters, we can assume
                    # it's not a valid TFCat type
                    raise TypeError(f"{type_} is not a TFCat type")
                tfcat_factory = getattr(tfcat.factory, type_)
                instance = tfcat_factory(**d)
            except (AttributeError, KeyError) as invalid:
                if strict:
                    msg = "Cannot coerce %r into a valid TFCat structure: %s"
                    msg %= (ob, invalid)
                    raise ValueError(msg)
                instance = ob
        return instance

    @property
    def is_valid(self):
        return not self.errors()

    def check_list_errors(self, checkFunc, lst):
        """Validation helper function."""
        # check for errors on each subitem, filter only subitems with errors
        results = (checkFunc(i) for i in lst)
        return [err for err in results if err]

    def errors(self):
        """Return validation errors (if any).
        Implement in each subclass.
        """

        # make sure that each subclass implements its own validation function
        if self.__class__ != Base:
            raise NotImplementedError(self.__class__)


