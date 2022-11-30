# -*- coding: utf-8 -*-
import sys
import os
import subprocess
import boto3

from sceptre.hooks import Hook
from sceptre.exceptions import InvalidHookArgumentSyntaxError

DEFAULT_REGION = 'us-west-2'

class SamDeploy(Hook):
    """
    A Sceptre Hook object for triggering the build and deploy of AWS SAM

    self.argument is parsed as a string of keyword args.
    After parsing, the following keywords are accepted:

    :location: Required. The location of the SAM code from within the project directory. (e.g. src/sam/)
    :config:   Required. The name of the config environment to use (e.g. dev)
    :region:   Optional. The AWS region. The default is us-west-2.

    Example:
        !deploy_sam location=src/same

    Note this hook requires Docker to be installed and its daemon should be running.
    """

    def __init__(self, *args, **kwargs):
        super(SamDeploy, self).__init__(*args, **kwargs)

    def run(self):
        kwargs = dict()
        for item in self.argument.split():
            k, v = item.split('=')
            kwargs[k] = v
        required_args = ['location', 'config']
        for arg in required_args:
            if not arg in kwargs:
                raise InvalidHookArgumentSyntaxError(
                    '{}: required kwarg "{}" not found'.format(__name__, arg)
                )

        region = kwargs.get('region', DEFAULT_REGION)

        os.chdir(kwargs['location'])
        print('{}: Building SAM application ...'.format(__name__))
        os.system('sam build')

        print('{}: Deploying SAM application ...'.format(__name__))
        os.system('sam deploy --config-env {}'.format(kwargs['config']))

def main():
    """
    test deploy_sam hook actions:
        python ./deploy_sam location=src/sam
    """

    request = SamDeploy(argument=' '.join(sys.argv[1:]))
    request.run()

if __name__ == '__main__':
    main()
