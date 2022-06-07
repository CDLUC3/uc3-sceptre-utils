# -*- coding: utf-8 -*-
from sceptre.resolvers import Resolver
from sceptre.exceptions import InvalidHookArgumentSyntaxError
from uc3_sceptre_utils.util import route53, DEFAULT_REGION


class HostedZoneId(Resolver):
    """
    Returns a AWS Route53 hosted zond Id given a domain name and a
    AWS region.  The region can be omitted in which case it defaults
    to 'us-east-1'.

    Example sceptre config usage:

    HostedZoneId: !route53_hostedzone_id ashley-demo.example.com us-west-2
    """

    def __init__(self, *args, **kwargs):
        super(HostedZoneId, self).__init__(*args, **kwargs)

    def resolve(self):
        if len(self.argument.split()) == 2:
            domain_name, region = self.argument.split()
        elif len(self.argument.split()) == 1:
            domain_name = self.argument
            region = DEFAULT_REGION
        else:
            raise InvalidHookArgumentSyntaxError(
                '{}: resolver requires either one or two positional parameters: '
                'domain_name [region]'.format(__name__)
            )

        hosted_zone_id = route53.get_hosted_zone_id(domain_name, region)
        if not hosted_zone_id:
            hosted_zone_id = str()
        self.logger.debug('{} - hosted_zone_id: {}'.format(__name__, hosted_zone_id))
        return hosted_zone_id
