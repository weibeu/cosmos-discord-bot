rules = {'color': 15277667,
 'fields': [{'inline': False,
             'name': '<a:pointer:440925289317531668>    ** Discord TOS apply**',
             'value': 'ANY violation will result in an immediate ban and report to Discord: [Discord '
                      'Tos](https://discordapp.com/tos)'},
            {'inline': False,
             'name': '<a:pointer:440925289317531668>    ** Be respectful of others**',
             'value': 'Bullying, cussing, harassment, racism, sexism, or any sort of discrimination will not be '
                      'tolerated.'},
            {'inline': False,
             'name': '<a:pointer:440925289317531668>    ** Use common sense**',
             'value': 'If someone is uncomfortable with something, stop. Also refrain from discussing real-life '
                      'Politics, religion, killing or suicide.'},
            {'inline': False,
             'name': '<a:pointer:440925289317531668>    ** Do not spam**',
             'value': 'Do not send random or irrelevant messages. This includes text, copypastas, Emojis, images, '
                      'links, literally anything. This applies to VC too, Ear-raping or being obnoxious in VC will '
                      'result in punishment.'},
            {'inline': False,
             'name': '<a:pointer:440925289317531668>    ** DRAMA FREE ZONE**',
             'value': 'Do not create server drama or take part in it. If you have any problem with the server, talk to '
                      'the staff via DMs.__**No roleplay**__'},
            {'inline': False,
             'name': '<a:pointer:440925289317531668>    ** No NSFW **',
             'value': 'Keep any and all 18+ flirting, overly sexual discussion, recommendations, images, links, etc. '
                      'in DM’s only.  NSFW content is not allowed on The Anime Discord and will result in an immediate ban.'},
            {'inline': False,
             'name': '<a:pointer:440925289317531668>    ** No Mini Modding **',
             'value': 'Leave all the moderation to Staff. If there is someone causing any trouble DM/Ping any of the '
                      'Staff Members preferably the online ones.'},
            {'inline': False,
             'name': '<a:pointer:440925289317531668>    ** Do not advertise or self-promote **',
             'value': 'This is not a place to advertise your server, YouTube, Twitch etc. Do not solicit other users '
                      'for donations or money. You will receive a permanent ban if we determine you are using the '
                      'server for those purposes.'},
            {'inline': False,
             'name': '<a:pointer:440925289317531668>    ** No inappropriate profiles **',
             'value': 'Usernames or avatars considered to be racist, discriminatory, overly lewd or intended to mimic '
                      'another user are not tolerated and will result in an immediate ban.'},
            {'inline': False,
             'name': '<a:pointer:440925289317531668>    ** Speak English **',      
             'value': 'This is an English speaking server.'},
            {'inline': False,
             'name': '<a:pointer:440925289317531668>    ** Respect channel topics and rules **',
             'value': 'Every channel on this server has its own specific guidelines and rules. They can be found in '
                      'the channel description.'},
            {'inline': False,
             'name': '<a:pointer:440925289317531668>    ** No Unbanning **',
             'value': 'Previously banned users can no longer appeal for an unban.'},
            {'inline': False,
             'name': '<a:pointer:440925289317531668>      ** Nickname Policy **',
             'value': 'We follow a nickname policy. Meaning if your nickname is NSFW we can and will change your nickname to something else.'},
            {'inline': False,
             'name': '<a:pointer:440925289317531668>    ** Dont organise raids **',
             'value': 'Members who are reported/seen organising raids and actually participate in them will be banned.'}],
'footer': {'icon_url': 'https://i.imgur.com/gEXjzvR.jpg',
            'proxy_icon_url': 'https://images-ext-1.discordapp.net/external/dCF2D_-HwWo85rIAC7x6hdiKSEfwn19Q-EwTBMd3Ri8/%3Fsize%3D1024/https/cdn.discordapp.com/icons/244998983112458240/d2702db072fdba5fd7be9123db9a668d.webp',
            'text': 'The Anime Discord'},
 'title': 'RULES',
 'type': 'rich'}

doggo = {'color': 15277667,
 'description': 'If one or more of the rules are broken by a member, the staff will be obligated to follow the bad '
                'doggo protocol:\n'
                '\n'
                '\t<a:arrow:437323076330586113> 😟 = First warning, lasts for 10 days. `+6 Hours doggo`\n'
                '\t<a:arrow:437323076330586113> 😠 = Second warning, lasts for 20 days. `+24 Hours doggo`\n'
                '\t<a:arrow:437323076330586113> 😡 = Third warning, lasts for 40 days. `+48 Hours doggo`\n'
                '\n'
                '\n'
                '__ If a member breaks the rules after being given 3rd warning, they will receive a **permanent '
                'ban**.__\n'
                '\n'
                '**Note:**\tA member may get banned despite not having above three warnings if their stay here causes '
                'a severe harm to the server or members in any possible manner.',
 'footer': {'icon_url': 'https://i.imgur.com/gEXjzvR.jpg',
            'proxy_icon_url': 'https://images-ext-1.discordapp.net/external/dCF2D_-HwWo85rIAC7x6hdiKSEfwn19Q-EwTBMd3Ri8/%3Fsize%3D1024/https/cdn.discordapp.com/icons/244998983112458240/d2702db072fdba5fd7be9123db9a668d.webp',
            'text': 'The Anime Discord'},
 'title': 'PUNISHMENTS',
 'type': 'rich'}

import colorsys

class Colour:
    """Represents a Discord role colour. This class is similar
    to an (red, green, blue) :class:`tuple`.
    There is an alias for this called Color.
    .. container:: operations
        .. describe:: x == y
             Checks if two colours are equal.
        .. describe:: x != y
             Checks if two colours are not equal.
        .. describe:: hash(x)
             Return the colour's hash.
        .. describe:: str(x)
             Returns the hex format for the colour.
    Attributes
    ------------
    value: :class:`int`
        The raw integer colour value.
    """

    __slots__ = ('value',)

    def __init__(self, value):
        if not isinstance(value, int):
            raise TypeError('Expected int parameter, received %s instead.' % value.__class__.__name__)

        self.value = value

    def _get_byte(self, byte):
        return (self.value >> (8 * byte)) & 0xff

    def __eq__(self, other):
        return isinstance(other, Colour) and self.value == other.value

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return '#{:0>6x}'.format(self.value)

    def __repr__(self):
        return '<Colour value=%s>' % self.value

    def __hash__(self):
        return hash(self.value)

    @property
    def r(self):
        """Returns the red component of the colour."""
        return self._get_byte(2)

    @property
    def g(self):
        """Returns the green component of the colour."""
        return self._get_byte(1)

    @property
    def b(self):
        """Returns the blue component of the colour."""
        return self._get_byte(0)

    def to_rgb(self):
        """Returns an (r, g, b) tuple representing the colour."""
        return (self.r, self.g, self.b)

    @classmethod
    def from_rgb(cls, r, g, b):
        """Constructs a :class:`Colour` from an RGB tuple."""
        return cls((r << 16) + (g << 8) + b)

    @classmethod
    def from_hsv(cls, h, s, v):
        """Constructs a :class:`Colour` from an HSV tuple."""
        rgb = colorsys.hsv_to_rgb(h, s, v)
        return cls.from_rgb(*(int(x * 255) for x in rgb))

    @classmethod
    def default(cls):
        """A factory method that returns a :class:`Colour` with a value of 0."""
        return cls(0)

    @classmethod
    def teal(cls):
        """A factory method that returns a :class:`Colour` with a value of ``0x1abc9c``."""
        return cls(0x1abc9c)

    @classmethod
    def dark_teal(cls):
        """A factory method that returns a :class:`Colour` with a value of ``0x11806a``."""
        return cls(0x11806a)

    @classmethod
    def green(cls):
        """A factory method that returns a :class:`Colour` with a value of ``0x2ecc71``."""
        return cls(0x2ecc71)

    @classmethod
    def dark_green(cls):
        """A factory method that returns a :class:`Colour` with a value of ``0x1f8b4c``."""
        return cls(0x1f8b4c)

    @classmethod
    def blue(cls):
        """A factory method that returns a :class:`Colour` with a value of ``0x3498db``."""
        return cls(0x3498db)

    @classmethod
    def dark_blue(cls):
        """A factory method that returns a :class:`Colour` with a value of ``0x206694``."""
        return cls(0x206694)

    @classmethod
    def purple(cls):
        """A factory method that returns a :class:`Colour` with a value of ``0x9b59b6``."""
        return cls(0x9b59b6)

    @classmethod
    def dark_purple(cls):
        """A factory method that returns a :class:`Colour` with a value of ``0x71368a``."""
        return cls(0x71368a)

    @classmethod
    def magenta(cls):
        """A factory method that returns a :class:`Colour` with a value of ``0xe91e63``."""
        return cls(0xe91e63)

    @classmethod
    def dark_magenta(cls):
        """A factory method that returns a :class:`Colour` with a value of ``0xad1457``."""
        return cls(0xad1457)

    @classmethod
    def gold(cls):
        """A factory method that returns a :class:`Colour` with a value of ``0xf1c40f``."""
        return cls(0xf1c40f)

    @classmethod
    def dark_gold(cls):
        """A factory method that returns a :class:`Colour` with a value of ``0xc27c0e``."""
        return cls(0xc27c0e)

    @classmethod
    def orange(cls):
        """A factory method that returns a :class:`Colour` with a value of ``0xe67e22``."""
        return cls(0xe67e22)

    @classmethod
    def dark_orange(cls):
        """A factory method that returns a :class:`Colour` with a value of ``0xa84300``."""
        return cls(0xa84300)

    @classmethod
    def red(cls):
        """A factory method that returns a :class:`Colour` with a value of ``0xe74c3c``."""
        return cls(0xe74c3c)

    @classmethod
    def dark_red(cls):
        """A factory method that returns a :class:`Colour` with a value of ``0x992d22``."""
        return cls(0x992d22)

    @classmethod
    def lighter_grey(cls):
        """A factory method that returns a :class:`Colour` with a value of ``0x95a5a6``."""
        return cls(0x95a5a6)

    @classmethod
    def dark_grey(cls):
        """A factory method that returns a :class:`Colour` with a value of ``0x607d8b``."""
        return cls(0x607d8b)

    @classmethod
    def light_grey(cls):
        """A factory method that returns a :class:`Colour` with a value of ``0x979c9f``."""
        return cls(0x979c9f)

    @classmethod
    def darker_grey(cls):
        """A factory method that returns a :class:`Colour` with a value of ``0x546e7a``."""
        return cls(0x546e7a)

    @classmethod
    def blurple(cls):
        """A factory method that returns a :class:`Colour` with a value of ``0x7289da``."""
        return cls(0x7289da)

    @classmethod
    def greyple(cls):
        """A factory method that returns a :class:`Colour` with a value of ``0x99aab5``."""
        return cls(0x99aab5)

Color = Colour

from discord import Embed, utils

class _EmptyEmbed:
    def __bool__(self):
        return False

    def __repr__(self):
        return 'Embed.Empty'

    def __len__(self):
        return 0

EmptyEmbed = _EmptyEmbed()

class EmbedProxy:
    def __init__(self, layer):
        self.__dict__.update(layer)

    def __len__(self):
        return len(self.__dict__)

    def __repr__(self):
        return 'EmbedProxy(%s)' % ', '.join(('%s=%r' % (k, v) for k, v in self.__dict__.items() if not k.startswith('_')))

    def __getattr__(self, attr):
        return EmptyEmbed


def from_dict(data):
    """Converts a :class:`dict` to a :class:`Embed` provided it is in the
    format that Discord expects it to be in.
    You can find out about this format in the `official Discord documentation`__.
    .. _DiscordDocs: https://discordapp.com/developers/docs/resources/channel#embed-object
    __ DiscordDocs_
    Parameters
    -----------
    data: :class:`dict`
        The dictionary to convert into an embed.
    """
    # we are bypassing __init__ here since it doesn't apply here
    self = Embed()

    # fill in the basic fields

    self.title = data.get('title', EmptyEmbed)
    self.type = data.get('type', EmptyEmbed)
    self.description = data.get('description', EmptyEmbed)
    self.url = data.get('url', EmptyEmbed)

    # try to fill in the more rich fields

    try:
        self._colour = Colour(value=data['color'])
    except KeyError:
        pass

    try:
        self._timestamp = utils.parse_time(data['timestamp'])
    except KeyError:
        pass

    for attr in ('thumbnail', 'video', 'provider', 'author', 'fields', 'image', 'footer'):
        try:
            value = data[attr]
        except KeyError:
            continue
        else:
            setattr(self, '_' + attr, value)

    return self