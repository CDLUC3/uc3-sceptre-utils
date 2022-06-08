# -*- coding: utf-8 -*-
"""
A sceptre hook to generate and validate AWS ACM certificates.

Required keyword arguments:

:action:            The action to perform.  Must be one of: "request" or "delete".
:cert_fqdn:         The domain name of the requested certificate.
:validation_domain: The DNS domain that validates this certificate request.  This must
                    match the domain of a valid AWS Route53 HostedZone.
:region:            The AWS region in which to create the certificate.

Optional Keyword arguments:

:subalt_names:      Additional subject alternative names for the certificate.
                    This can be a comma separated list of domain names.

Example sceptre config usage:

hooks:
  before_create:
    - !acm_certificate
        action: request
        cert_fqdn: ashley-demo.example.com
        validation_domain: example.com
        region: us-east-1
        subalt_names: www.ashley-demo.example.com,adem.example.com
  after_delete:
    - !acm_certificate
        action: delete
        cert_fqdn: ashley-demo.example.com
        validation_domain: example.com
        region: us-east-1
"""

import sys
import time
import re

from sceptre.cli.helpers import setup_logging
from sceptre.hooks import Hook
from sceptre.exceptions import InvalidHookArgumentSyntaxError
from uc3_sceptre_utils.util import acm, route53


class AcmCertificate(Hook):
    def __init__(self, *args, **kwargs):
        super(AcmCertificate, self).__init__(*args, **kwargs)

    def _usage(self):
        print(__doc__)

    def _handle_cert_request(self, cert_fqdn, subalt_names, validation_domain, region):
        """
        Handle certificate request process.  Allow time for cert to be
        auto-signed.  Times out after 5 minutes.
        """
        acm.request_cert(cert_fqdn, subalt_names, validation_domain, region)
        tries = 0
        max_tries = 30
        interval = 10
        while tries < max_tries:
            time.sleep(interval)
            cert = acm.get_cert_object(cert_fqdn, region)
            if cert['Status'] != 'ISSUED':
                tries += 1
                self.logger.info('{} - Request status: {}'.format(
                    __name__, cert['Status'])
                )
            else:
                break
        self.logger.info('{} - Cert: {} - Status: {}'.format(
            __name__, cert_fqdn, cert['Status'])
        )
        return

    def run(self):
        # parse self.argument string
        self.logger.info('{} - self.argument: {}'.format(__name__, self.argument))
        required_args = ['action', 'cert_fqdn', 'validation_domain', 'region']
        missing = []
        for arg in required_args:
            if arg not in self.argument:
                missing.append(arg)
        if missing:
            self._usage()
            raise InvalidHookArgumentSyntaxError(
                '{}: some required keyword arguments are missing: {}'.format(__name__, missing))
        if 'subalt_names' in self.argument:
            subalt_names = self.argument['subalt_names'].split(',')
        else:
            subalt_names = []
        action = self.argument['action']
        cert_fqdn = self.argument['cert_fqdn']
        validation_domain = self.argument['validation_domain']
        region = self.argument['region']
        self.logger.info('{} -  parsed args:- action: {}, cert_fqdn: {}, subalt_names: {}, validation_domain: {}, region: {}'.format(__name__, action, cert_fqdn, subalt_names, validation_domain, region))

        # determine certificate status and handle accordingly
        cert = acm.get_cert_object(cert_fqdn, region)
        if cert is not None:
            self.logger.info('{} - get_cert_object - cert: {}'.format( __name__, cert))
        if action == 'request':
            if not cert:
                self.logger.info('{} - Requesting certificate for {}'.format(
                    __name__, cert_fqdn)
                )
                self._handle_cert_request(cert_fqdn, subalt_names, validation_domain, region)

            elif cert['Status'] == 'ISSUED':
                self.logger.info('{} - Cert: {} - Status: {}'.format(
                    __name__, cert_fqdn, cert['Status'])
                )

            elif cert['Status'] == 'PENDING_VALIDATION':
                self.logger.info('{} - Cert: {} - Status: {}'.format(
                    __name__, cert_fqdn, cert['Status'])
                )
                if ("ValidationMethod" in cert["DomainValidationOptions"] and
                        cert["DomainValidationOptions"]["ValidationMethod"] == "DNS"):
                    acm.request_validation(cert, validation_domain, region)

            elif cert['Status'] == 'VALIDATION_TIMED_OUT':
                self.logger.info('{} - Cert: {} - Status: {}'.format(
                    __name__, cert_fqdn, cert['Status'])
                )
                self.logger.info('{} - Deleting certificate: {}'.format(
                    __name__, cert['CertificateArn'])
                )
                acm.delete_cert(cert['CertificateArn'], region=region)
                self.logger.info('{} - Re-requesting certificate: {}'.format(
                    __name__, cert_fqdn)
                )
                self._handle_cert_request(cert_fqdn, subalt_names, validation_domain, region)

            elif cert['Status'] == 'FAILED':
                raise RuntimeError('ACM certificate request failed: {}'.format(
                    cert['FailureReason']))

            elif cert['Status'] == 'REVOKED':
                raise RuntimeError('ACM certificate is in revoked state: {}'.format(
                    cert['RevocationReason']))

            else:
                raise RuntimeError('ACM certificate status is {}'.format(cert['Status']))

        elif action == 'delete':
            if cert:
                self.logger.info('{} - Deleting certificate: {}'.format(
                    __name__, cert['CertificateArn'])
                )
                acm.delete_cert(cert['CertificateArn'], region=region)

            # clean up route53 certificate validation CNAME entry
            if not cert_fqdn.endswith('.'):
                cert_fqdn += '.'
            validation_cname_pattern=re.compile(r'_\w{32}\.' + re.escape(cert_fqdn))
            record_set = route53.get_resource_record_set(
                hosted_zone=validation_domain,
                record_type='CNAME',
                pattern=validation_cname_pattern,
            )
            if isinstance(record_set, list):
                raise RuntimeError('multiple certificate validation CNAME record sets '
                'found matching "{}"'.format(cert_fqdn)
            )
            if record_set:
                self.logger.info('{} - Deleting route53 certificate validation '
                    'CNAME: {}'.format(__name__, cert_fqdn)
                )
                route53.change_record_set(record_set, validation_domain, 'DELETE')

        else:
            raise InvalidHookArgumentSyntaxError(
                '{}: value of kwarg "action" must be one of '
                '"request, delete"'.format(__name__)
            )


def main():
    """
    test acm_certificate hook actions:
        python ./acm_certificate.py \
                action=request \
                cert_fqdn=testing00.blee.red \
                subalt_names=testing.blee.red,www.testing.blee.red \
                validation_domain=blee.red \
                region=us-east-1

    """

    request = AcmCertificate(argument=' '.join(sys.argv[1:]))
    request.logger = setup_logging(True, False)
    request.run()

if __name__ == '__main__':
    main()


