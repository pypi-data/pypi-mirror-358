from importlib.metadata import version

# try to get version from package (if installed)
try:
    VERSION = version('PyWebDAV3-GNUHealth')
except BaseException:
    # Not running from installed version
    VERSION = "DEVELOPMENT"

# author hardcoded here
AUTHOR = 'Andrew Leech <andrew@alelec.net>, Simon Pamies <spamsch@gmail.com>'
