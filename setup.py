from setuptools import setup, find_packages

setup(
    name='uc3-sceptre-utils',
    packages=find_packages('.'),
    entry_points={
        'sceptre.hooks': [
            'account_verifier = uc3_sceptre_utils.hooks.account_verifier:AccountVerifier',
            'acm_certificate = uc3_sceptre_utils.hooks.acm_certificate:AcmCertificate',
            'ecs_cluster = uc3_sceptre_utils.hooks.ecs_cluster:ECSCluster',
            'ecs_task_exec_role = uc3_sceptre_utils.hooks.ecs_task_exec_role:ECSTaskExecRole',
            'route53_hosted_zone = uc3_sceptre_utils.hooks.route53:Route53HostedZone',
            's3_bucket = uc3_sceptre_utils.hooks.s3_bucket:S3Bucket',
            'sam_deploy = uc3_sceptre_utils.hooks.sam_deploy:SamDeploy',
        ],
        'sceptre.resolvers': [
            'acm_certificate_arn = uc3_sceptre_utils.resolvers.acm_certificate_arn:AcmCertificateArn',
            'package_version = uc3_sceptre_utils.resolvers.package_version:PackageVersion',
            'hosted_zone_id = uc3_sceptre_utils.resolvers.hosted_zone_id:HostedZoneId',
            'ssm_parameter = uc3_sceptre_utils.resolvers.ssm_parameter:SsmParameter',
        ],
    },
)
