# -*- coding: utf-8 -*-
import boto3
from uc3_sceptre_utils.util import DEFAULT_REGION


def get_hosted_zone_id(domain_name, region=DEFAULT_REGION):
    """
    Return the hosted zoned Id corresponding to 'domain_name'.
    """
    route53_client = boto3.client('route53', region_name=region)
    response = route53_client.list_hosted_zones(
        HostedZoneType='PrivateHostedZone'
    )
    hosted_zones = response["HostedZones"]
    while response["IsTruncated"]:
        response = route53_client.list_hosted_zones(
            Marker=response["NextMarker"]
        )
        hosted_zones += response["HostedZones"]
    if not domain_name.endswith("."):
        domain_name += "."
    hosted_zone_ids = [
        zone['Id'] for zone in hosted_zones if zone['Name'] == domain_name
    ]
    if len(hosted_zone_ids) > 1:
        raise RuntimeError(
            "Found multiple matching hosted zones: {}".format(hosted_zone_ids)
        )
    if len(hosted_zone_ids) < 1:
        return None
    return hosted_zone_ids[0].split("/")[2]


def get_elb_hosted_zone_id(elb_arn):
    """
    Return the canonical hosted zoned Id of the given loadbalance arn.
    """
    elb_client = boto3.client('elbv2')
    response = elb_client.describe_load_balancers(LoadBalancerArns=[elb_arn])
    return response['LoadBalancers'][0]['CanonicalHostedZoneId']


def get_resource_record_set(
        hosted_zone,
        record_type=None,
        pattern=None,
        domain_name=None):
    """
    Return route53 resource_record_set by name.

    :domain_name:
    :hosted_zone: domainname of the route53 hosted zone to query
    """

    # collect all record sets in hosted zone
    client = boto3.client('route53')
    hosted_zone_id = get_hosted_zone_id(hosted_zone)
    response = client.list_resource_record_sets(HostedZoneId=hosted_zone_id)
    records = response['ResourceRecordSets']
    if 'IsTruncated' in response:
        while response['IsTruncated']:
            response = client.list_resource_record_sets(
                HostedZoneId=hosted_zone_id,
                StartRecordName=response['NextRecordName'],
                StartRecordType=response['NextRecordType'],
            )
            records.append(response['ResourceRecordSets'])

    # filter for record set Type
    if record_type:
        records = [r for r in records if r['Type'] == record_type]

    # filter for domain_name or pattern
    if domain_name:
        records = [r for r in records if r['Name'] == domain_name]
    elif pattern:
        records = [r for r in records if pattern.match(r['Name'])]
    else:
        raise ValueError("must supply either 'domain_name' or 'pattern'")
    if len(records) == 0:
        return None
    elif len(records) == 1:
        return records[0]
    return records


def change_record_set(
        record_set,
        validation_domain,
        action='UPSERT',
        comment=str(),
        region=DEFAULT_REGION):
    """
    Change route53 record.
    """
    valid_actions = ('CREATE', 'DELETE', 'UPSERT')
    if action not in valid_actions:
        raise ValueError('"action" must be one of {}'.format(valid_actions))
    route53_client = boto3.client('route53', region_name=region)
    hosted_zone_id = get_hosted_zone_id(validation_domain, region)
    change_batch = {
        'Comment': comment,
        'Changes': [
            {
                'Action': action,
                'ResourceRecordSet': record_set,
            }
        ]
    }
    route53_client.change_resource_record_sets(
        HostedZoneId=hosted_zone_id,
        ChangeBatch=change_batch,
    )
