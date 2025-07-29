from tfcat.base import Base


class Observation(Base):
    """
    Represents a TF observation
    """

    def __init__(self, # id=None,
                 geometry=None, properties=None, **extra):
        """
        Initialises a Feature object with the given parameters.

        :param id: Feature identifier, such as a sequential number.
        :type id: str, int
        :param geometry: Geometry corresponding to the feature.
        :param properties: Dict containing properties of the feature.
        :type properties: dict
        :return: Observation object
        :rtype: Observation
        """
        super(Observation, self).__init__(**extra)
        # if id is not None:
        #    self["id"] = id
        self["geometry"] = (self.to_instance(geometry, strict=True)
                            if geometry else None)
        self["properties"] = properties or {}

    def errors(self):
        geo = self.get('geometry')
        return geo.errors() if geo else None


class ObservationCollection(Base):
    """
    Represents a FeatureCollection, a set of multiple Feature objects.
    """

    def __init__(self, observations, **extra):
        """
        Initialises a FeatureCollection object from the

        :param observations: List of features to constitute the FeatureCollection.
        :type observations: list
        :return: ObservationCollection object
        :rtype: ObservationCollection
        """
        super(ObservationCollection, self).__init__(**extra)
        self["observations"] = observations

    def errors(self):
        return self.check_list_errors(lambda x: x.errors(), self.features)

    def __getitem__(self, key):
        try:
            return self.get("observations", ())[key]
        except (KeyError, TypeError, IndexError):
            return super(Base, self).__getitem__(key)

