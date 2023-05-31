# constants.py
from typing import List
from snowplow_tracker import _version, SelfDescribingJson

VERSION = "py-%s" % _version.__version__
DEFAULT_ENCODE_BASE64 = True
BASE_SCHEMA_PATH = "iglu:com.snowplowanalytics.snowplow"
MOBILE_SCHEMA_PATH = "iglu:com.snowplowanalytics.mobile"
SCHEMA_TAG = "jsonschema"
CONTEXT_SCHEMA = "%s/contexts/%s/1-0-1" % (BASE_SCHEMA_PATH, SCHEMA_TAG)
UNSTRUCT_EVENT_SCHEMA = "%s/unstruct_event/%s/1-0-0" % (BASE_SCHEMA_PATH, SCHEMA_TAG)
ContextArray = List[SelfDescribingJson]
