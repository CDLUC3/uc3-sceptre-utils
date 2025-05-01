#!/usr/bin/env python
import boto3
from uc3_sceptre_utils.util import DEFAULT_REGION
from uc3_sceptre_utils.util.route53 import get_hosted_zone_id

import sys
#import json

domain_name = sys.argv[1]
print(domain_name)
hosted_zone_id = get_hosted_zone_id(domain_name)
print(hosted_zone_id)
