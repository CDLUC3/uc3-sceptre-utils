# -*- coding: utf-8 -*-
import sys
import os
import subprocess
import boto3

from sceptre.hooks import Hook
from sceptre.exceptions import InvalidHookArgumentSyntaxError

DEFAULT_REGION = 'us-west-2'

class DockerToEcr(Hook):
    """
    A Sceptre Hook object for packaging an application as a Docker image and pushing the image to ECR.

    self.argument is parsed as a string of keyword args.
    After parsing, the following keywords are accepted:

    :ecr_name: Required. SSM key for the parameter containing the ECR name (e.g. /uc3/dmp/hub/dev/EcrName).
                         Example parameter value: 'my-ecr'
    :ecr_uri:  Required. SSM key for the parameter containing the ECR URI (e.g. /uc3/dmp/hub/dev/EcrUri).
                         Example parameter value: '01234567.dkr.ecr.us-west-2.amazonaws.com/my-ecr'
    :location: Required. The location of the folder, from wihtin the project dir, that contains the
                         Dockerfile. (e.g. src/my_app)
    :region:   Optional. The AWS region. The default is us-west-2.

    Example:
        !docker_to_ecr ecr_name=/uc3/svc/sub-svc/env/EcrName ecr_uri=/uc3/svc/sub-svc/env/EcrUri location=src/my_app

    Note this hook requires Docker to be installed and its daemon should be running.
    """

    def __init__(self, *args, **kwargs):
        super(DockerToEcr, self).__init__(*args, **kwargs)

    def run(self):
        kwargs = dict()
        for item in self.argument.split():
            k, v = item.split('=')
            kwargs[k] = v
        required_args = ['ecr_name', 'ecr_uri', 'location']
        for arg in required_args:
            if not arg in kwargs:
                raise InvalidHookArgumentSyntaxError(
                    '{}: required kwarg "{}" not found'.format(__name__, arg)
                )

        region = kwargs.get('region', DEFAULT_REGION)
        ecr_name = self.fetch_ssm_parameter(kwargs['ecr_name'])
        ecr_uri = self.fetch_ssm_parameter(kwargs['ecr_uri'])
        ecr_short_uri = ecr_uri.replace(ecr_name, '').split('/')[0]

        print('{}: Logging into ECR ...'.format(__name__))
        os.system('aws ecr get-login-password --region {} | docker login --username AWS --password-stdin {}'.format(region, ecr_short_uri))

        cwd = subprocess.run('pwd', stdout=subprocess.PIPE, text=True)
        lambda_path = os.path.join(cwd.stdout.strip(), kwargs['location'])

        print("{}: Building Docker image in: {} ...".format(__name__, lambda_path))
        os.chdir(lambda_path)
        os.system('docker build -t {} .'.format(ecr_name))
        os.system('docker tag {}:latest {}:latest'.format(ecr_name, ecr_uri))

        print("{}: Pushing Docker image to ECR: {}:latest ...".format(__name__, ecr_uri))
        os.system('docker push {}:latest'.format(ecr_uri))

    def fetch_ssm_parameter(_self, key):
      ssm = boto3.client('ssm')
      try:
          response = ssm.get_parameter(Name=key, WithDecryption=True)
      except Exception:
          print('{} - parameter name not found: {}'.format(__name__, key))
          return None
      return response['Parameter']['Value']

def main():
    """
    test docker_to_ecr hook actions:
        python ./docker_to_ecr ecr_name=/uc3/svc/sub-svc/env/EcrName ecr_uri=/uc3/svc/sub-svc/env/EcrUri location=src/my_app
    """

    request = DockerToEcr(argument=' '.join(sys.argv[1:]))
    request.run()

if __name__ == '__main__':
    main()
