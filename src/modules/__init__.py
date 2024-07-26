# Alternative to Pyrogram Plugins
# Implement all using the wanted order

from . import guidelines
from . import connection
from . import mimic


def implement():
    guidelines.implement()
    connection.implement()
    mimic.implement()
