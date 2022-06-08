# -*- coding: utf-8 -*-
import time
import boto3
from uc3_sceptre_utils.util import route53, DEFAULT_REGION


def get_cert_arn(cert_fqdn, region=DEFAULT_REGION):
    """
    Return the ACM Certificate ARN for 'cert_fqdn'.
    """
    acm_client = boto3.client('acm', region_name=region)
    response = acm_client.list_certificates()
    cert_list = response['CertificateSummaryList']
    while 'NextToken' in response:
        response = acm_client.list_certificates(NextToken=response['NextToken'])
        cert_list += response['CertificateSummaryList']
    arn_list = [
        cert['CertificateArn'] for cert in cert_list
        if cert['DomainName'] == cert_fqdn
    ]
    if len(arn_list) > 1:
        raise RuntimeError(
            "Found multiple matching ACM certificates: {}".format(arn_list)
        )
    if len(arn_list) < 1:
        return None
    return arn_list[0]


def get_cert_object(cert_fqdn, region=DEFAULT_REGION):
    """
    Return the ACM certificate object for 'cert_fqdn'.
    """
    acm_client = boto3.client('acm', region_name=region)
    certificate_arn = get_cert_arn(cert_fqdn, region)
    if certificate_arn:
        return acm_client.describe_certificate(
            CertificateArn=certificate_arn
        )['Certificate']
    else:
        return None


def request_cert(cert_fqdn, subalt_names, validation_domain, region=DEFAULT_REGION):
    """
    Create a ACM certificate request.  Create validation record set in route53.
    'validation_domain' must match a valid Route53 HostedZone. 
    """
    hosted_zone_id = route53.get_hosted_zone_id(validation_domain, region)
    if hosted_zone_id is not None:
        validation_method = 'DNS'
    else:
        raise RuntimeError(
                "No Route53 HostedZone matches 'validation_domain: {}".format(validation_domain))
    acm_client = boto3.client('acm', region_name=region)
    domain_validation_options = [
            dict(DomainName=cert_fqdn, ValidationDomain=validation_domain)]
    for domain in subalt_names:
        domain_validation_options.append(dict(DomainName=domain, ValidationDomain=validation_domain))
    response = acm_client.request_certificate(
        DomainName=cert_fqdn,
        ValidationMethod=validation_method,
        SubjectAlternativeNames=subalt_names,
        IdempotencyToken='request_cert',
        DomainValidationOptions=domain_validation_options,
    )
    arn = response['CertificateArn']
    cert = acm_client.describe_certificate(CertificateArn=arn)['Certificate']
    while 'ResourceRecord' not in cert['DomainValidationOptions'][0]:
        time.sleep(5)
        cert = acm_client.describe_certificate(CertificateArn=arn)['Certificate']
    cert_validation_record_set(
        cert['DomainValidationOptions'][0]['ResourceRecord'],
        validation_domain
    )


def delete_cert(cert_arn, region=DEFAULT_REGION):
    """Delete an existing ACM certificate."""
    acm_client = boto3.client('acm', region_name=region)
    acm_client.delete_certificate(CertificateArn=cert_arn)
    return


def cert_validation_record_set(resource_record, validation_domain, action='UPSERT'):
    """
    Create/delete route53 record set for ACM certificate validation.
    """
    record_set = {
        'Name': resource_record['Name'],
        'Type': resource_record['Type'],
        'TTL': 300,
        'ResourceRecords': [
            {
                'Value': resource_record['Value'],
            },
        ],
    }
    route53.change_record_set(
        record_set,
        validation_domain,
        action,
        'acm cert validation',
    )


def request_validation(cert, validation_domain, region=DEFAULT_REGION):
    """
    Resubmit certificate validation request based upon the validation
    options of a certificate (i.e. method is either DNS or EMAIL).
    """
    validation_options = cert['DomainValidationOptions'][0]
    if validation_options['ValidationMethod'] == 'DNS':
        route53.create_validation_record_set(
            validation_options['ResourceRecord'],
            validation_domain,
            region,
        )
    else:
        acm_client = boto3.client('acm', region_name=region)
        acm_client.resend_validation_email(
            CertificateArn=cert['CertificateArn'],
            Domain=cert['DomainName'],
            ValidationDomain=validation_domain,
        )
    return
