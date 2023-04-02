import logging
import typing

import marshmallow

from divisions.common import utils as common_utils

logger = logging.getLogger(__name__)

_LOG_PREFIX = "[FAB-COMMON-SERVICE]"


def validate_data_schema(
    data: typing.Union[dict, typing.List[dict]],
    schema: marshmallow.schema.Schema,
) -> typing.Optional[dict]:
    try:
        validated_data = schema.load(data=data, unknown=marshmallow.EXCLUDE)
    except marshmallow.exceptions.ValidationError as e:
        logger.error(
            "{} Provided data does not comply with validation schema. Errors: {}.".format(
                _LOG_PREFIX, common_utils.get_exception_message(exception=e)
            )
        )
        return None

    return validated_data
