import lyricsgenius as genius
from cogs.utils.util import get_config

class Lyrics(object):
    """Fetch lyrics, artists and song info from Genius."""
    _CAT = get_config()["GENIUS_CLIENT_ACCESS_TOKEN"]

    def __init__(self):
        
