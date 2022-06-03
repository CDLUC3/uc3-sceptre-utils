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
        ],
        'sceptre.resolvers': [
            'certificate_arn = uc3_sceptre_utils.resolvers.certificate_arn:CertificateArn',
            'package_version = uc3_sceptre_utils.resolvers.package_version:PackageVersion',
        ],
    },
)
