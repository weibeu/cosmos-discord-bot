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
             'name': '<a:pointer:440925289317531668>    ** Do not advertise or self-promote. **',
             'value': 'This is not a place to advertise your server, YouTube, Twitch etc. Do not solicit other users '
                      'for donations or money. You will receive a permanent ban if we determine you are using the '
                      'server for those purposes.'},
            {'inline': False,
             'name': '<a:pointer:440925289317531668>    ** No inappropriate profiles **',
             'value': 'Usernames or avatars considered to be racist, discriminatory, overly lewd or intended to mimic '
                      'another user are not tolerated and will result in an immediate ban.'},
            {'inline': False,
             'name': '<a:pointer:440925289317531668>            ** Speak English **',      
             'value': 'This is an English speaking server.'},
            {'inline': False,
             'name': '<a:pointer:440925289317531668>    ** Respect channel topics and rules. **',
             'value': 'Every channel on this server has its own specific guidelines and rules. They can be found in '
                      'the channel description.'},
            {'inline': False,
             'name': '<a:pointer:440925289317531668>            ** No Unbanning **',
             'value': 'Previously banned users can no longer appeal for an unban.'},
            {'inline': False,
             'name': '<a:pointer:440925289317531668>      ** Nickname Policy **',
             'value': 'We follow a nickname policy. Meaning if your nickname is NSFW we can and will change your nickname to something else.'},
            {'inline': False,
             'name': '<a:pointer:440925289317531668>    ** Dont organise raids. **',
             'value': 'Members who are reported/seen organising raids and actually participate in them will be banned.'}],
'footer': {'icon_url': 'https://cdn.discordapp.com/icons/244998983112458240/d2702db072fdba5fd7be9123db9a668d.webp?size=1024',
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
 'footer': {'icon_url': 'https://cdn.discordapp.com/icons/244998983112458240/d2702db072fdba5fd7be9123db9a668d.webp?size=1024',
            'proxy_icon_url': 'https://images-ext-1.discordapp.net/external/dCF2D_-HwWo85rIAC7x6hdiKSEfwn19Q-EwTBMd3Ri8/%3Fsize%3D1024/https/cdn.discordapp.com/icons/244998983112458240/d2702db072fdba5fd7be9123db9a668d.webp',
            'text': 'The Anime Discord'},
 'title': 'PUNISHMENTS',
 'type': 'rich'}

from discord import Embed

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