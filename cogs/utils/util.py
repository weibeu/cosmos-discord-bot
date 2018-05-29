from discord import Embed
from random import choice
from json import load
import giphy_client
from giphy_client.rest import ApiException
def get_config():
    with open("settings/config.json") as config_file:
        config = load(config_file)
        return config
colors = {"red": "F44336", "pink": "E91E63", "purple": "9C27B0", "deep-purple": "673AB7", "indigo": "3F51B5", "blue": "2196F3", "light-blue": "03A9F4", "cyan": "00BCD4", "teal": "009688", "green": "4CAF50", "light-green": "8BC34A", "lime": "CDDC39", "yellow": "FFEB3B", "amber": "FFC107", "orange": "FF9800", "deep-orange": "FF5722", "grey": "9E9E9E", "black": "000000", "white": "FFFFFF"}
giphy = giphy_client.DefaultApi()
giphy_api_key = get_config()["giphy_api_key"]



def get_random_color():
    return colors[choice(list(colors.keys()))]

def get_random_embed_color():
    return int("0x"+get_random_color(), 16)

def get_random_gif():
    try:
        response = giphy.gifs_random_get(giphy_api_key)
    except Exception as e:
        print("Error fetching random gif from giphy")
    return response.data.image_original_url

def get_gif(query):
    try:
        response = giphy.gifs_search_get(giphy_api_key, query, limit=7)
    except Exception as e:
        print("Error fetching {0} gif from giphy".format(query))
    return choice(response.data)._images.original.url

def get_trending_gif():
    try:
        response = giphy.gifs_trending_get(giphy_api_key)
    except Exception as e:
        print("Error fetching trending gif")
    return choice(response.data)._images.original.url

def get_reaction_numbers():
    r_n = {'1': 'one:436147947021926400', '2': 'two:436147947500208139', '3': 'three:436148355366649867', '4': 'four:436148381921050634', '5': 'five:436148404742258688', '6': 'six:436148439168843777', '7': 'seven:436148470357819412', '8': 'eight:436148492852002816', '9': 'nine:436148515396124672', '10': 'ten:436148536476827671', '11': 'eleven:436171645804347393', '12': 'twelve:436171647053987840', '13': 'thirteen:436171650405367810', '14': 'fourteen:436171653274271769', '15': 'fifteen:436171654343819274', '16': 'sixteen:436171848934490113', '17': 'seventeen:436171850050175007', '18': 'eighteen:436171851702599681', '19': 'nineteen:436171851710988288', '20': 'twenty:436171929330909184', '21': 'twentyone:436172095693520896', '22': 'twentytwo:436172096368934912', '23': 'twentythree:436172097782415361', '24': 'twentyfour:436172097941667841', '25': 'twentyfive:436172099531309057', '26': 'twentysix:436172100722622465', '27': 'twentyseven:436172218750468107', '28': 'twentyeight:436172221816504340', '29': 'twentynine:436172223238111233', '30': 'thirty:436172265135144962', '31': 'thirtyone:436172306826657792', '32': 'thirtytwo:436172308080623627', '33': 'thirtythree:436172394223239178', '34': 'thirtyfour:436172461621510164', '35': 'thirtyfive:436172462523285504', '36': 'thirtysix:436172463433449472', '37': 'thirtyseven:436172522179002398', '38': 'thirtyeight:436172522644570112', '39': 'thirtynine:436172524452315156', '40': 'forty:436172560481255425', '41': 'fortyone:436172596460126208', '42': 'fortytwo:436172597655371778', '43': 'fortythree:436172600742379520', '44': 'fortyfour:436172649106898944', '45': 'fortyfive:436172652240044033', '46': 'fortysix:436172659647315969', '47': 'fortyseven:436172698700218378', '48': 'fortyeight:436172702215307274', '49': 'fortynine:436172703754616832', '50': 'fifty:436172760499224589'}
    return r_n
def get_reaction_yes_no():
    return {"yes": 'yes:436133316119494657', "no": 'no:436133317461540865'}

def tick(opt, label=None):
    emoji = '<:yes:436133316119494657>' if opt else '<:no:436133317461540865>'
    if label is not None:
        return f'{emoji}: {label}'
    return emoji
