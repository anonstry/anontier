# Alternative to Pyrogram Plugins
# Implement all using the wanted order

from src.modules import guidelines
from src.modules import connection
from src.modules import mimic


def implement():
    guidelines.implement()
    connection.implement()
    mimic.implement()
