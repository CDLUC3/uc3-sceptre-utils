# -*- coding: utf-8 -*-
import sys
import os
import subprocess
import boto3

from sceptre.hooks import Hook
from sceptre.exceptions import InvalidHookArgumentSyntaxError

DEFAULT_REGION = 'us-west-2'
DEFAULT_ECR_TAG_PREFIX = 'latest'

class DockerToEcr(Hook):
    """
    A Sceptre Hook object for packaging an application as a Docker image and pushing the image to ECR.

    self.argument is parsed as a string of keyword args.
    After parsing, the following keywords are accepted:

    :dockerfile_dir: Required. The location of the folder, from wihtin the project dir, that contains the
                         Dockerfile. (e.g. src/my_app)
    :ssm_path:       Required. The SSM path where we will find our other variables (e.g. /uc3/dmp/hub/dev/)
    :ecr_name:       Required. SSM key for the parameter containing the ECR name (e.g. EcrName).
                         Example parameter value: 'my-ecr'
    :ecr_uri:        Required. SSM key for the parameter containing the ECR URI (e.g. EcrUri).
                         Example parameter value: '01234567.dkr.ecr.us-west-2.amazonaws.com/my-ecr'
    :ecr_tag_prefix: Optional. The ECR tag prefix. Default is 'latest'
    :region:         Optional. The AWS region. Default is 'us-west-2'

    Example:
        !docker_to_ecr dockerfile_dir=src/my_app ssm_path=/uc3/dmp/hub/env/ ecr_name=EcrName ecr_uri=EcrUri

    Note this hook requires Docker to be installed and its daemon should be running.
    """

    def __init__(self, *args, **kwargs):
        super(DockerToEcr, self).__init__(*args, **kwargs)

    def run(self):
        kwargs = dict()
        for item in self.argument.split():
            k, v = item.split('=')
            kwargs[k] = v
        required_args = ['dockerfile_dir', 'ssm_path', 'ecr_name', 'ecr_uri']
        for arg in required_args:
            if not arg in kwargs:
                raise InvalidHookArgumentSyntaxError(
                    '{}: required kwarg "{}" not found'.format(__name__, arg)
                )

        region = kwargs.get('region', DEFAULT_REGION)
        ecr_tag_prefix = kwargs.get('ecr_tag_prefix', DEFAULT_ECR_TAG_PREFIX)

        ecr_name = self.fetch_ssm_parameter(kwargs['ssm_path'], kwargs['ecr_name'])
        ecr_uri = self.fetch_ssm_parameter(kwargs['ssm_path'], kwargs['ecr_uri'])
        ecr_short_uri = ecr_uri.replace(ecr_name, '').split('/')[0]

        print('{}: Logging into ECR {} ...'.format(__name__, ecr_short_uri))
        logged_in = os.system('aws ecr get-login-password --region {} | docker login --username AWS --password-stdin {}'.format(region, ecr_short_uri))

        print('NAME: {}, URI: {}'.format(ecr_name, ecr_uri))

        if logged_in == 0:
            cwd = subprocess.run('pwd', stdout=subprocess.PIPE, text=True)
            dockerfile_path = os.path.join(cwd.stdout.strip(), kwargs['dockerfile_dir'])

            print("{}: Building Docker image in: {} ...".format(__name__, dockerfile_path))
            os.chdir(dockerfile_path)
            built = os.system('docker build -t {} .'.format(ecr_name))

            if built == 0:
                os.system('docker tag {}:{} {}:{}'.format(ecr_name, ecr_tag_prefix, ecr_uri, ecr_tag_prefix))

                print("{}: Pushing Docker image to ECR: {}:{} ...".format(__name__, ecr_uri, ecr_tag_prefix))
                os.system('docker push {}:{}'.format(ecr_uri, ecr_tag_prefix))
            else:
                print('{} - Unable to build Docker image. Cannot upload to ECR until this has been fixed!'.format(__name__))
        else:
            print('{} - Unable to login to ECR! Make sure your AWS credentials are set.'.format(__name__))

    def fetch_ssm_parameter(_self, base_path, key):
      ssm = boto3.client('ssm')

      ssm_path_parts = base_path.strip().split('/')
      ssm_path_parts.append(key)
      key_name = '/'.join(ssm_path_parts).replace('//', '/')

      try:
          response = ssm.get_parameter(Name=key_name, WithDecryption=True)
      except Exception:
          print('{} - parameter name not found: {}'.format(__name__, key_name))
          return None
      return response['Parameter']['Value']

def main():
    """
    test docker_to_ecr hook actions:
        python !docker_to_ecr dockerfile_dir=src/my_app ssm_path=/uc3/dmp/hub/env/ ecr_name=EcrName ecr_uri=EcrUri
    """

    request = DockerToEcr(argument=' '.join(sys.argv[1:]))
    request.run()

if __name__ == '__main__':
    main()
