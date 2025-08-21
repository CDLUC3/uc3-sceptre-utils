# -*- coding: utf-8 -*-
from sceptre.resolvers import Resolver
from sceptre.exceptions import InvalidHookArgumentSyntaxError
from uc3_sceptre_utils.util import route53


class HostedZoneId(Resolver):
    """
    Returns a AWS Route53 public hosted zone Id given a domain name and a
    AWS region.  The region can be omitted in which case it defaults
    to the sceptre stack_group_config.region.

    Example sceptre config usage:

    HostedZoneId: !hosted_zone_id ashley-demo.example.com
    """

    def __init__(self, *args, **kwargs):
        super(HostedZoneId, self).__init__(*args, **kwargs)

    def resolve(self):
        self.logger.info('{} - self.stack: {}'.format(__name__, self.stack))
        self.logger.info('{} - self.argument: {}'.format(__name__, self.argument))
        # not used:
        #profile = self.stack.profile

        if len(self.argument.split()) == 2:
            domain_name, region = self.argument.split()
        elif len(self.argument.split()) == 1:
            domain_name = self.argument
            region = self.stack.region
        else:
            raise InvalidHookArgumentSyntaxError(
                '{}: resolver requires either one or two positional parameters: '
                'domain_name [region]'.format(__name__)
            )

        #self.logger.info('{} - region: {}'.format(__name__, region))
        hosted_zone_id = route53.get_hosted_zone_id(domain_name, region)
        if not hosted_zone_id:
            hosted_zone_id = str()
        self.logger.info('{} - hosted_zone_id: {}'.format(__name__, hosted_zone_id))
        return hosted_zone_id
