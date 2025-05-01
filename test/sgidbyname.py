#!/usr/bin/env python
import sys
import json
import boto3


def main():
    sg_name = sys.argv[1]
    print(sg_name)
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
        print('{} - securitygroup name not found: {}'.format(__name__, sg_name))
        return None

    value = response['SecurityGroups'][0]['GroupId']
    return value


if __name__ == '__main__':
    sg_id = main()
    #print(json.dumps(sg_id, indent=4))
    print(sg_id)

