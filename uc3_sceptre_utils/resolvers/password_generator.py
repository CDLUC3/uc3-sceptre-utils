# -*- coding: utf-8 -*-
import random
import string

from sceptre.resolvers import Resolver
from sceptre.exceptions import InvalidHookArgumentSyntaxError
from uc3_sceptre_utils.util import route53, DEFAULT_REGION


class PasswordGenerator(Resolver):
    """
    Returns a random password based on the following arguments:
      0 - integer - length
      1 - boolean - whether or not to include special characters

    Example sceptre config usage:
      RdsPassword: !password_generator 12, true
    """

    def __init__(self, *args, **kwargs):
        super(PasswordGenerator, self).__init__(*args, **kwargs)

    def resolve(self):
        if len(self.argument.split()) == 2:
          length, allow_chars = self.argument.split()
        else:
          raise InvalidHookArgumentSyntaxError(
            '{}: Resolver requires two arguments: length (Int) and allow special chars (Bool) - '
              'For example: 8 false'.format(__name__)
          )

        try:
          int(length)
        except ValueError:
          raise InvalidHookArgumentSyntaxError(
            '{}: Invalid argument! Resolver requires two arguments: length (Int) and allow special chars (Bool) - '
              'For example: 8 false'.format(__name__)
          )
        else:
          size = int(length)

        chars = string.ascii_letters + string.digits

        if allow_chars.lower() == 'true':
          # Use a limited subset of special chars since many DB systems have reserved chars
          chars = chars + '~!#$^&*_-+=|:'

        password = ''.join(random.choice(chars) for i in range(size))
        print("Generated random password of length ", size, " is: ", password)
        return password
