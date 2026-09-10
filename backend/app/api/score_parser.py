import json
from decimal import Decimal

from marshmallow import missing
from webargs.flaskparser import FlaskParser


class ScoreJSONParser(FlaskParser):
    """Preserve decimal JSON tokens before score precision validation.

    Used by the table/game blueprints. Other numeric schema fields still
    deserialize through their existing Marshmallow fields.
    """

    def _raw_load_json(self, req):
        if not req.is_json:
            return missing
        return json.loads(req.get_data(cache=True), parse_float=Decimal)
