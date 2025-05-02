# uc3-sceptre-utils
Custom hooks and resolvers for use with sceptre

## Installation

This install sets up full scepter installation and requirements including:
- sceptre
- boto3
- sceptre-ssm-resolver
- sceptre-aws-resolver


### Prereqs

a python virtual environment running python 3.11 or higher.


### Install
```bash
git clone git@github.com:CDLUC3/uc3-sceptre-utils.git
pip install -e uc3-sceptre-utils/
```


### Update
```bash
cd uc3-sceptre-utils/
git pull
pip install -e uc3-sceptre-utils/
```


## Available Resolvers

### hosted_zone_id

Returns a AWS Route53 public hosted zone Id given a domain name and a AWS region.
```yaml
# sceptre config
parameters:
  HostedZoneId: !hosted_zone_id uc3dev.cdlib.org

```

### securitygroup_id_by_name

Given a SecurityGroup name, returns the corresponding EC2 SecurityGroupId:
```yaml
# sceptre config
parameters:
  SecurityGroups:
    - !securitygroup_id_by_name default
    - !securitygroup_id_by_name dmp-tool-stg-codebuild-data-migration-SecGrp
```
