# -*- coding: utf-8 -*-
import boto3
from sceptre.resolvers import Resolver
from sceptre.exceptions import InvalidHookArgumentSyntaxError


class SecurityGroupIdByName(Resolver):
    """

    Returns the corresponding EC2 SecurityGroupId , or `None` if not found.

    Example sceptre config usage:
        default_sg: !securitygroup_id_by_name default

    Parameters
    ----------
    argument: sg_name
        The name of the ec2 security group
    stack: sceptre.stack.Stack
    """

    def __init__(self, argument, stack=None):
        super(SecurityGroupIdByName, self).__init__(argument, stack)

    def resolve(self):
        if len(self.argument.split()) == 1:
            sg_name = self.argument
        else:
            raise InvalidHookArgumentSyntaxError(
                '{}: resolver requires one positional parameter: '
                'parameter_name'.format(__name__)
            )
        ec2_client = boto3.client('ec2')
        try:
            response = ec2_client.describe_security_groups(
                Filters=[
                    {
                        'Name': 'group-name',
                        'Values': [sg_name],
                    }
                ]
            )
        except Exception:
            self.logger.info('{} - securitygroup name not found: {}'.format(__name__, sg_name))
            return None
        value = response['SecurityGroups'][0]['GroupId']
        self.logger.info('{} - securitygroup id for {}: {}'.format(__name__, sg_name, value))
        return value
