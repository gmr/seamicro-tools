"""
Main Application Controller

"""
import argparse
import getpass
import logging
import paramiko
import sys

from seamicro_tools import tech_support_bundle

LOGGER = logging.getLogger(__name__)


class SeamicroClient(object):
    """Main application class that handles cli args and invoking modules for
    processing.

    """
    def __init__(self):
        """Create a new instance of the Seamicro Client"""
        self.channel = None
        self.connection = None
        self.options = None
        self.running = True

    def cli_options(self):
        """Build the argument parser and parse the CLI options returning them.
        If no password is supplied, use getpass to prompt the user for it.

        :rtype: argparse.Namespace

        """
        options = {'description': 'Tools to ease Seamicro Administration'}
        parser = argparse.ArgumentParser(**options)
        parser.add_argument('host',
                            help='The chassis administration host',
                            action='store')
        parser.add_argument('-u', '--user',
                            help='The username to login with. Default: admin',
                            action='store',
                            default='admin')
        parser.add_argument('-p',
                            '--password',
                            help='The password to use when authenticating. If '
                                 'blank you will be prompted for the password.',
                            action='store')
        parser.add_argument('--hostname',
                            help='The internal seamicro chassis hostname. '
                                 'Default: seamicro',
                            default='seamicro',
                            action='store')

        subparsers = parser.add_subparsers(dest='action')
        tsb = subparsers.add_parser('tech-support-bundle',
                                    help='Generate a tech support bundle')
        tsb.add_argument('-c', '--case',
                         help='The existing support case #',
                         action='store')
        tsb.add_argument('-d', '--destination',
                         help='The directory to place the files',
                         action='store')
        tsb.add_argument('-e', '--extended',
                         help='Send additional, more in-depth logs',
                         action='store_true')

        args = parser.parse_args()

        if not args.password:
            args.password = getpass.getpass('Password: ')

        return args

    def close(self):
        """Close the open paramiko session"""
        self.running = False
        self.channel.close()
        self.connection.close()
        LOGGER.info('Connection closed')

    def connect(self):
        """Connect to the Seamicro Chassis using the options passed in returning
        the SSHClient and Channel objects to communicate with.

        :param argparse.Namespace options: The CLI options
        :rtype: paramiko.SSHClient, paramiko.Channel

        """
        LOGGER.info("Logging into %s as %s",
                    self.options.host, self.options.user)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.load_system_host_keys()
        ssh.connect(self.options.host,
                    username=self.options.user,
                    password=self.options.password)
        return ssh, ssh.invoke_shell()

    def enable(self):
        """Enable the session for configuration or other administration
        commands.

        """
        LOGGER.info("Enabling %s", self.options.hostname)
        self.wait_for_enable_prompt()
        self.send('enable\n')
        self.wait_for_enabled_prompt()
        LOGGER.info("Enabled")

    def run(self):
        """Invoked by running the application, core logic for running the app"""
        self.options = self.cli_options()
        try:
            self.connection, self.channel = self.connect()
        except paramiko.AuthenticationException as error:
            LOGGER.error('Error logging into %s as %s: %s',
                         self.options.host, self.options.user, error)
            sys.exit(1)

        try:
            self.enable()
        except KeyboardInterrupt:
            LOGGER.info('Aborted')
            self.close()
            sys.exit(1)

        # Handle tech-support bundle requests
        if self.options.action == 'tech-support-bundle':
            try:
                return tech_support_bundle.run(self)
            except KeyboardInterrupt:
                LOGGER.info('Aborted')
                self.close()
                sys.exit(1)

    def send(self, value):
        """Send a value to the channel

        :param str value: The value to send

        """
        self.channel.send(value)

    @property
    def enable_prompt(self):
        """Return the format of the enable prompt

        :rtype: str

        """
        return '%s>' % self.options.hostname

    @property
    def enabled_prompt(self):
        """Return the format of the enabled prompt

        :rtype: str

        """
        return '%s#' % self.options.hostname

    def read_until_value(self, value):
        """Read input until value is matched where value is a str to match

        :param channel paramiko.Channel: The channel to read off of
        :param str value: The value to read until
        :rtype: str

        """
        data_in = ''
        while self.running:
            if self.channel.recv_ready():
                data_in += self.channel.recv(1024)
                if isinstance(value, str):
                    if value in data_in:
                        break
        return data_in

    def read_until_enabled_prompt(self):
        """Read from the seamicro until the enabled prompt is sent back.

        :rtype: str

        """
        return self.read_until_value(self.enabled_prompt)

    def wait_for_enable_prompt(self):
        """Read until the enable prompt on input but don't return anything"""
        self.read_until_value(self.enable_prompt)

    def wait_for_enabled_prompt(self):
        """Read until the enabled prompt on input but don't return anything"""
        self.read_until_value(self.enabled_prompt)


def main():
    # Set the logging level and formatter
    logging.basicConfig(level=logging.INFO,
                        format="%(message)s")

    # Disable paramiko's output for most everything
    paramiko_logger = logging.getLogger('paramiko')
    paramiko_logger.setLevel(level=logging.CRITICAL)

    # Create the seamicro client and run it
    client = SeamicroClient()
    client.run()
