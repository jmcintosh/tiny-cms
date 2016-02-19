
from ConfigParser import ConfigParser

# Instantiate config
config = ConfigParser()

# Parse config file
config.read('config.ini')

print config.get('database', 'connection_string')