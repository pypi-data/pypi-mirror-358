import jsonschema
from json import loads, load
import urllib.request
import ssl

_context = ssl._create_unverified_context()
JSONSCHEMA_URI = "https://voparis-ns.obspm.fr/maser/tfcat/v1.0/schema#"
TOPCAT_TFCAT_URL = "http://andromeda.star.bristol.ac.uk/releases/topcat/pre/topcat-full_tfcat.jar"


def tfcat_schema(schema_uri=JSONSCHEMA_URI):
    with urllib.request.urlopen(schema_uri, context=_context) as f:
        return loads(f.read().decode())


def validate(instance, schema_uri=JSONSCHEMA_URI):
    """Validate TFCat object

    :param instance: TFCat object
    :param schema_uri: URI of TFCat JSON schema
    """
    jsonschema.validate(instance, schema=tfcat_schema(schema_uri))


def validate_file(file_name, schema_uri=JSONSCHEMA_URI):
    """Validate TFCat data from file.

    :param file_name: TFCat data file name
    :type file_name: Path or str
    :param schema_uri: URI of TFCat JSON schema
    :type schema_uri: str
    """
    with open(file_name, 'r') as f:
        validate(load(f), schema_uri)
