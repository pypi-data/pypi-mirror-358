from requests import HTTPError
import quartic_sdk.utilities.constants as Constants
from datetime import datetime
from typing import Union
from pytz import timezone
import logging

_logger = logging.getLogger(__name__)


class Rule:
    """
    This helper class is used for creating and validating raw_json needed for creation of
    RuleDefinition schema for Procedure/ProcedureStep
    """
    # raw_json key types used for creating rule
    TAG = '0'
    OPERATOR = '1'

    def __init__(self, client, name, first_tag, operator, second_tag, duration_ms):
        """
        Rule class constructor
        :param client: client which is used for calling API
        :param name: Rule Name
        :param first_tag: Tag(Tag Entity) Object
        :param operator: Operator used for creating rule condition like '0' for PLUS, '1' for MINUS and so on
        :param second_tag: Tag(Tag Entity) Object
        :param duration_ms: Duration of rule in milliseconds
        """
        self.client = client
        self.name = name
        self.first_tag = first_tag
        self.operator = operator
        self.second_tag = second_tag
        self.duration_ms = duration_ms

    def raw_json(self):
        """
        This method returns raw_json schema required for RuleDefinition creation
        :return: Json Schema
        """
        return {
            "0": {
                self.TAG: str(self.first_tag.id)
            },
            "1": {
                self.OPERATOR: self.operator
            },
            "2": {
                self.TAG: str(self.second_tag.id)
            }
        }

    def rule_schema(self):
        """
        This method returns schema required for RuleDefinition creation
        :return: Json Schema
        """
        return {
            "name": self.name,
            "raw_json": self.raw_json(),
            "duration_ms": self.duration_ms,
            "tags": [self.first_tag.id, self.second_tag.id],
            "category": Constants.OTHERS
        }

    def validate_rule_raw_json(self):
        """
        This is used to validate raw_json schema
        """
        try:
            self.client.api_helper.call_api(
                Constants.POST_RULE_VALIDATE_JSON,
                method_type=Constants.API_POST,
                body={"raw_json": self.raw_json()}
            )
        except HTTPError as exception:
            raise Exception(f'Exception in validating rule: {exception.response.content.decode()}')


def to_epoch(date: datetime, timezone_string: Union[str, None] = None) -> Union[int, None]:
    """
    Converts datetime objects to epoch timestamps. If the timezone string is passed then that
    timezone is used to convert the object while converting to epoch value.
    :param date: An aware datetime.datetime object.
    :param timezone_string: A string representing the timezone.

    :return: The epoch timestamp value.
    """
    if not date:
        return date

    if timezone_string:
        try:
            # Label the datetime object with the user timezone. This will not do any
            # addition/subtraction.
            date = timezone(timezone_string).localize(date)
        except Exception:
            _logger.exception("Invalid timezone string found! Using system time!")

    return int(date.timestamp() * 1000.)
