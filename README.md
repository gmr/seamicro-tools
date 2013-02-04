seamicro-tools
==============

Command line application for automating or easing the use of the administration
console. Currently only supports generating the files requested by tech support
but will include other commands (as I finish porting them over) such as powering
on and off servers.

Installation
------------
Run "python setup.py install" in the main directory which will install a
seamicro-tools script in a common path.

Currently supported commands
----------------------------

 - tech-support-bundle: Generate the files requested by Seamicro when opening a support case

Example Use
-----------

    bash$ seamicro-tools admin.seamicro.myhost.com tech-support-bundle -c c-1234 -d ~/Desktop/c-1234

Command Line Options
--------------------

    positional arguments:
      host                  The chassis administration host
      {tech-support-bundle}
        tech-support-bundle
                            Generate a tech support bundle

    optional arguments:
      -h, --help              show this help message and exit
      -u USER, --user USER    The username to login with. Default: admin
      -p PASSWORD, --password PASSWORD
                              The password to use when authenticating. If blank you
                              will be prompted for the password.
      --hostname HOSTNAME     The internal Seamicro chassis hostname. Default:
                              seamicro

    tech-support-bundle optional arguments:
      -c CASE, --case CASE    The existing support case #
      -d DESTINATION, --destination DESTINATION
                              The directory to place the files
      -e, --extended          Send additional, more in-depth logs
