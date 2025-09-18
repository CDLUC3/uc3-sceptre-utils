# -*- coding: utf-8 -*-
import re

from sceptre.hooks import Hook
from sceptre.exceptions import SceptreException
from sceptre.exceptions import InvalidHookArgumentSyntaxError


class AccountVerifier(Hook):
    """
    Test if the Id of currently authenticated AWS account matches
    the specified account Id.  

    Usage in stack config:

        hooks:
          before_create:
            - !account_verifier 123412341234

    """

    def __init__(self, *args, **kwargs):
        super(AccountVerifier, self).__init__(*args, **kwargs)

    def run(self):
        """
        Compare argument to AWS Account Id.

        :raises: InvalidHookArgumentSyntaxError, if argument is not a valid 
                 AWS Account Id.
        """

        configured_account_id = str(self.argument)
        #self.logger.info('{} - self.stack: {}'.format(__name__, self.stack))
        #self.logger.info('{} - self.argument: {}'.format(__name__, self.argument))
        #self.logger.info('{} - configured_account_id: {}'.format(__name__, configured_account_id))

        account_id_re = re.compile(r'\d{12}')
        if not (configured_account_id and account_id_re.match(configured_account_id)):
            raise InvalidHookArgumentSyntaxError(
                '{}: argument "{}" is not a valid AWS account Id.'.format(
                    __name__, configured_account_id
                )
            )

        response = self.stack.connection_manager.call(
            service="sts",
            command="get_caller_identity",
        )
        actual_account_id = response["Account"]

        if not actual_account_id == configured_account_id:
            raise SceptreException(
                '{}: account verification failed - current account {} does '
                'not match specified account Id {}.'.format(
                    __name__, actual_account_id, configured_account_id
                )
            )
        else:
            self.logger.debug(
                '{} - verification succeeded for Id {}'.format(__name__, actual_account_id)
            )
            return True
