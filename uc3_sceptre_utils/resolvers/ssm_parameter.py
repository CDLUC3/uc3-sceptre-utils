# -*- coding: utf-8 -*-
import boto3
from sceptre.resolvers import Resolver
from sceptre.exceptions import InvalidHookArgumentSyntaxError


class SsmParameter(Resolver):
    """
    Returns value from SSM ParamaterStore, or `None` if parameter_name not found.

    Example sceptre config usage:
        my_ssm_var: !ssm_parameter /uc3/ops/demo/my_param
    """

    def __init__(self, *args, **kwargs):
        super(SsmParameter, self).__init__(*args, **kwargs)

    def resolve(self):
        if len(self.argument.split()) == 1:
            parameter_name = self.argument
        else:
            raise InvalidHookArgumentSyntaxError(
                '{}: resolver requires either one positional parameter: '
                'parameter_name'.format(__name__)
            )
        ssm_client = boto3.client('ssm')
        try:
            response = ssm_client.get_parameter(
                Name=parameter_name,
                WithDecryption=True
            )
        except Exception:
            self.logger.info('{} - parameter name not found: {}'.format(__name__, parameter_name))
            return None
        value = response['Parameter']['Value']
        self.logger.info('{} - ssm parameter for {}: {}'.format(__name__, parameter_name, value))
        return value
