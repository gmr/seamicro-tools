"""
Generate a tech support bundle, outputting the files tech supports requests to
a specified directory

"""
import logging
import os

LOGGER = logging.getLogger(__name__)


def compose_filename(prefix, key, case):
    """Create a filename for the specified prefix, key and case

    :rtype: str

    """
    filename = '%(prefix)s/%(key)s.txt'
    if case:
        filename = '%(prefix)s/%(key)s-%(case)s.txt'
    return os.path.normpath(filename % {'prefix': prefix,
                                        'key': key,
                                        'case': case})


def run(controller):
    """Run the tech_support_bundle command, generating the files that tech
    support generally requests (in my experience).

    :param seamicro_tools.controller.SeamicroClient controller: The main app

    """
    # Set the prefix for where to store the support files
    prefix = '.'
    if controller.options.destination:
        prefix = controller.options.destination

    # Base commands
    commands = {'tech-support-detail': 'show tech-support detail',
                'logging': 'show logging',
                'console': 'show console'}

    # Add additional output if extended is flagged
    if controller.options.extended:
        commands['chassis'] = 'show chassis'
        commands['version'] = 'show version details'
        commands['storage-disk'] = 'show storage disk brief'
        commands['storage-pool'] = 'show storage pool brief'
        commands['storage-volume'] = 'show storage volume brief'
        commands['storage-assign'] = 'show storage assign brief'

    # Iterate through each command to run, saving out the file
    for key in commands.keys():
        # If a user cancels halfway through, don't process the rest
        if controller.running:
            filename = compose_filename(prefix, key, controller.options.case)
            LOGGER.info('Processing %s, writing to %s', key, filename)
            with open(filename, 'w') as handle:
                controller.send('%s | nomore\n' % commands[key])
                value = controller.read_until_enabled_prompt()
                if value:
                    handle.write(value)
            LOGGER.info('Completed %s', key)
