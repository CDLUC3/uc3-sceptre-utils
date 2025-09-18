# uc3-sceptre-utils
Custom hooks and resolvers for use with sceptre

## Installation

This install sets up full scepter installation and requirements including:
- sceptre
- boto3
- sceptre-ssm-resolver
- sceptre-aws-resolver
- yq


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
The region can be omitted in which case use the sceptre `stack_group_config.region`.
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


## Available Hooks

### Account Verifier

Verify the AWS Account ID before performing stack change actions.  If the configured account ID 
differs from the active account in which secptre is executing, sceptre will fail.

Set the allowed Account ID in sceptre environment config:
```yaml
---
# config/dev/config.yaml
#
domain: uc3dev.cdlib.net
account_id: '123412341234'
```

Run `account_verifier` hook in scepter stack config:
```yaml
# config/dev/aoss-security.yaml
---
template:
  path: aoss-security.yaml.j2

hooks:
  before_validate:
    - !account_verifier {{ stack_group_config.account_id }}
  before_create:
    - !account_verifier {{ stack_group_config.account_id }}
  before_update:
    - !account_verifier {{ stack_group_config.account_id }}

```
