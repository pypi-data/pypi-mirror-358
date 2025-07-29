import json
import tfcat.factory
import tfcat.base
import numpy

"""
This file is adapted from: https://github.com/jazzband/geojson/blob/master/geojson/codec.py
"""


class TFCatEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, numpy.signedinteger) or isinstance(obj, numpy.unsignedinteger):
            return int(obj)
        elif isinstance(obj, numpy.floating):
            return float(obj)
        else:
            return tfcat.factory.Base.to_instance(obj) # NOQA

# Wrap the functions from json, providing encoder, decoders, and
# object creation hooks.
# Here the defaults are set to only permit valid JSON as per RFC 4267


def _enforce_strict_numbers(obj):
    raise ValueError("Number %r is not JSON compliant" % obj)


def dump(obj, fp, cls=TFCatEncoder, allow_nan=False, **kwargs):
    return json.dump(obj, fp, cls=cls, allow_nan=allow_nan, **kwargs)


def dumps(obj, cls=TFCatEncoder, allow_nan=False, **kwargs):
    return json.dumps(obj, cls=cls, allow_nan=allow_nan, **kwargs)


def load(fp,
         cls=json.JSONDecoder,
         parse_constant=_enforce_strict_numbers,
         object_hook=tfcat.base.Base.to_instance,
         **kwargs):
    return json.load(fp,
                     cls=cls, object_hook=object_hook,
                     parse_constant=parse_constant,
                     **kwargs)


def loads(s,
          cls=json.JSONDecoder,
          parse_constant=_enforce_strict_numbers,
          object_hook=tfcat.base.Base.to_instance,
          **kwargs):
    return json.loads(s,
                      cls=cls, object_hook=object_hook,
                      parse_constant=parse_constant,
                      **kwargs)


