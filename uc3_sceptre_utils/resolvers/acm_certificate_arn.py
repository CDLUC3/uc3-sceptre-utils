# -*- coding: utf-8 -*-
from sceptre.resolvers import Resolver
from sceptre.exceptions import InvalidHookArgumentSyntaxError
from uc3_sceptre_utils.util import acm

DEFAULT_REGION = 'us-east-1'


class AcmCertificateArn(Resolver):
    """
    Returns a AWS ACM certificate ARN given a domain name and a
    AWS region.  The region can be omitted in which case it defaults
    to 'us-east-1'.

    Example sceptre config usage:

    CertARN: !acm_certificate_arn ashley-demo.example.com us-west-2
    """

    def __init__(self, *args, **kwargs):
        super(AcmCertificateArn, self).__init__(*args, **kwargs)

    def resolve(self):
        if len(self.argument.split()) == 2:
            cert_fqdn, region = self.argument.split()
        elif len(self.argument.split()) == 1:
            cert_fqdn = self.argument
            region = DEFAULT_REGION
        else:
            raise InvalidHookArgumentSyntaxError(
                '{}: resolver requires either one or two positional parameters: '
                'cert_fqdn [region]'.format(__name__)
            )

        arn = acm.get_cert_arn(cert_fqdn, region)
        if not arn:
            arn = str()
        self.logger.debug('{} - certificate_arn: {}'.format(__name__, arn))
        return arn
