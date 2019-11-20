import discord
from discord.ext import commands

import asyncio
import async_timeout
import datetime
import humanize as humnum
import json
import math
import random
import re
import subprocess
import uuid
import youtube_dl

from itertools import islice
from .utils.handler import DownloadError
from .utils.paginators import SimplePaginator
from cogs.utils.genius import Genius
from cogs.utils.util import get_random_embed_color

if not discord.opus.is_loaded():
    discord.opus.load_opus('libopus.so')

def get_duration(url):
    cmd = f'ffprobe -v error -show_format -of json {url}'
    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    data = json.loads(output)
    try:
        duration = data['format']['duration']

        process.kill()

        return math.ceil(float(duration))
    except:
        pass


def outtmpl_seed():
    ytid = str(uuid.uuid4()).replace('-', '')
    return str(int(ytid, 16))


ffmpeg_options = {
    'before_options': '-nostdin',
    'options': '-vn'
    }


def has_permissions_or_dj(**perms):
    def predicate(ctx):

        try:
            player = ctx.bot.get_cog('music').players[ctx.guild.id]
        except KeyError:
            return False

        if ctx.author.id == player.dj.id:
            return True

        ch = ctx.channel
        permissions = ch.permissions_for(ctx.author)

        missing = [perm for perm, value in perms.items() if getattr(permissions, perm, None) != value]

        if not missing:
            return True

        raise commands.MissingPermissions(missing)
    return commands.check(predicate)


class MusicSource(discord.PCMVolumeTransformer):

    def __init__(self, source, *, data, volume, filename):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')
        self.duration = data.get('duration') or get_duration(data.get('url'))
        self.weburl = data.get('webpage_url')
        self.views = data.get('view_count')
        self.thumb = data.get('thumbnail')
        self.requester = data.get('requester')
        self.channel = data.get('channel')
        self.stream = data.get('stream')
    
        self.filename = filename

    @classmethod
    async def from_filename(cls, *, data, filename, volume):
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data, filename=filename,
                   volume=volume)


class YTDLSource(discord.PCMVolumeTransformer):
    """A class which uses YTDL to retrieve a song and returns it as a source for Discord."""
    def __init__(self, source, *, data, volume, filename):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')
        try:
            self.duration = data.get('duration') or get_duration(data.get('url'))
            self.weburl = data.get('webpage_url')
            self.views = data.get('view_count')
            self.thumb = data.get('thumbnail')
            self.requester = data.get('requester')
            self.channel = data.get('channel')
        except:
            pass
        try:
            self.stream = data.get('stream')
        except:
            pass

        self.filename = filename

    @classmethod
    async def from_url(cls, entry, *, loop=None, player=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        url = entry.query
        chan = entry.channel
        ctx = entry.ctx
        playl_msg = None
        opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{chan.id}/{outtmpl_seed()}%(extractor)s_%(id)s.%(ext)s',
            'restrictfilenames': True,
            'noplaylist': False,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'auto',
            'playlistend': 30,
            'source_address': '0.0.0.0'
        }

        ytdl = youtube_dl.YoutubeDL(opts)

        if stream:
            entry.stream = True
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
            if 'entries' in data:
                # take first item from a playlist
                data = data['entries'][0]

            data['requester'] = entry.requester
            data['channel'] = entry.channel
            data['stream'] = True
            filename = data['url'] if stream else ytdl.prepare_filename(data)
            await player.queue.put(cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data, filename=filename, volume=1))
            await chan.send(f"```css\nAdded {data['title']} to queue.```", delete_after=7)
            if not player.waiting:
                return

            if player.now_playing and player.queue.qsize() < 4:
                await player.playing_controller(player.entry)
            return

        ytdl.params['extract_flat'] = True
        ef_info = ytdl.extract_info(download=False, url=url)
        ytdl.params['extract_flat'] = False

        if 'entries' in ef_info:
            length = len(ef_info['entries'])
        else:
            length = 1
        for v in range(1, length + 1):
            try:
                ytdl.params.update({'playlistend': v, 'playliststart': v})
                data = await loop.run_in_executor(None, ytdl.extract_info, url)
            except Exception as e:
                if length <= 1:
                    raise DownloadError(f':: {e}')
                else:
                    continue

            if 'entries' in data:
                data = data['entries'][0]

            if length == 1:
                await chan.send(f'```ini\n[Added: {data["title"]} to the queue.]\n```', delete_after=15)
            elif not playl_msg:
                playl_msg = await chan.send(f'```ini\n[Adding your playlist to the queue.]\n```', delete_after=30)

            data['requester'] = entry.requester
            data['channel'] = entry.channel
            data['stream'] = False

            filename = ytdl.prepare_filename(data)
            await player.queue.put(cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data,
                                       filename=filename, volume=player.volume))

            if player.waiting:
                if player.now_playing and player.queue.qsize() < 4:
                    await player.playing_controller(player.entry)


class MusicPlayer:
    """Music Player instance.
    Each guild using music will have a separate instance."""

    def __init__(self, bot, ctx):
        self.bot = bot

        self.queue = asyncio.Queue()
        self.next = asyncio.Event()
        self.die = asyncio.Event()
        self.killing = None

        self.entry = None
        self.held = None
        self.guild = ctx.guild
        self.default_chan = ctx.channel
        self.dj = None
        self.volume = 1

        self.waiting = None
        self.now_playing = None
        self.paused_msg = None
        self.react_task = None

        self.player_task = self.bot.loop.create_task(self.player_loop())
        self.inactive_task = self.bot.loop.create_task(self.inactive_check(ctx))

        self.controls = {'▶': 'resume',
                         '⏸': 'pause',
                         '⏹': 'stop',
                         '⏭': 'skip',
                         '🔀': 'shuffle',
                         '🔂': 'repeat',
                         '➕': 'vol_up',
                         '➖': 'vol_down',
                         'ℹ': 'queue'}

        self.shuffling = None
        self.skips = set()
        self.repeats = set()
        self.shuffles = set()

    async def inactive_check(self, ctx):
        ctx = ctx
        await self.die.wait()
        ctx.author = ctx.guild.me
        try:
            await ctx.invoke(self.bot.get_command('fstop'))
        except Exception as e:
            print(e)

    async def player_loop(self):
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            self.next.clear()

            try:
                with async_timeout.timeout(600):
                    self.entry = await self.queue.get()

                    try:
                        self.held.cleanup()
                    except AttributeError:
                        pass

                    self.held = self.entry
            except asyncio.TimeoutError:
                try:
                    self.held.cleanup()
                except AttributeError:
                    pass

                try:
                    self.entry.cleanup()
                except AttributeError:
                    pass

                await self.default_chan.send('I have been inactive for 10 minutes. Goodbye!', delete_after=60)
                return self.die.set()

            self.guild.voice_client.play(self.entry, after=lambda s: self.bot.loop.call_soon_threadsafe(self.next.set))
            await self.playing_controller(self.entry)

            self.waiting = True
            await self.next.wait()
            self.waiting = False

            while self.shuffling:
                await asyncio.sleep(1)

            while self.killing:
                await asyncio.sleep(1)

            self.shuffles.clear()
            self.skips.clear()
            self.repeats.clear()

            await asyncio.sleep(.5)

    async def nowplaying_check(self, chan):
        try:
            async for m in chan.history(limit=5):
                if m.id == self.now_playing.id:
                    return True
        except (discord.HTTPException, AttributeError):
            return False
        return False

    async def playing_controller(self, entry):

        try:
            self.react_task.cancel()
        except AttributeError:
            pass

        if entry.stream:
            tit = "🔴 | Now Streaming"
        else:
            tit = "Now Playing"
        embed = discord.Embed(title=tit, description=entry.title, colour=get_random_embed_color())
        embed.set_thumbnail(url=entry.thumb if entry.thumb is not None else 'http://i.imgur.com/EILyJR6.png')
        embed.add_field(name='Requested by', value=entry.requester.mention)
        embed.add_field(name='Video URL', value=f"[Click Here!]({entry.weburl})")
        if not entry.stream\
                :
            embed.add_field(name='Duration', value=str(datetime.timedelta(seconds=int(entry.duration))))
        embed.add_field(name='Queue Length', value=f'{self.queue.qsize()}')
        if self.dj:
            embed.add_field(name='Current DJ:', value=self.dj.mention)

        if self.queue.qsize() > 0:
            data = '\n'.join(f'**-** `{v.title[0:50]}{"..." if len(v.title) > 50 else ""}`\n{"-"*10}'
                             for v in islice(self.queue._queue, 0, 3, None))

            embed.add_field(name='Coming Up:', value=data, inline=False)
        embed.set_footer(text=f'🎶 | Views: {humnum.intcomma(entry.views)}')

        if not await self.nowplaying_check(entry.channel) and self.now_playing:
            try:
                await self.now_playing.delete()
            except discord.HTTPException:
                pass

            self.now_playing = await entry.channel.send(embed=embed)
        elif not self.now_playing:
            self.now_playing = await entry.channel.send(embed=embed)
        else:
            self.react_task = self.bot.loop.create_task(self.react_controller(entry))
            return await self.now_playing.edit(embed=embed, content=None)

        for x in self.controls.keys():
            try:
                await self.now_playing.add_reaction(x)
            except (discord.HTTPException, discord.InvalidArgument):
                pass

        self.react_task = self.bot.loop.create_task(self.react_controller(entry))

    async def react_controller(self, entry):
        vc = entry.channel.guild.voice_client

        def check(r, u):

            if not self.now_playing:
                return False

            elif str(r) not in self.controls.keys():
                return False

            elif u.id == self.bot.user.id or r.message.id != self.now_playing.id:
                return False

            elif u not in vc.channel.members:
                return False

            return True

        while self.now_playing:

            if vc is None:
                return self.react_task.cancel()

            react, user = await self.bot.wait_for('reaction_add', check=check)
            control = self.controls.get(str(react))

            try:
                await self.now_playing.remove_reaction(react, user)
            except discord.HTTPException:
                pass

            cmd = self.bot.get_command(control)
            ctx = await self.bot.get_context(react.message)
            ctx.author = user

            try:
                if cmd.is_on_cooldown(ctx):
                    pass
                if not await self.invoke_react(cmd, ctx):
                    pass
                else:
                    self.bot.loop.create_task(ctx.invoke(cmd))
            except Exception as e:
                ctx.command = self.bot.get_command('reactcontrol')
                await cmd.dispatch_error(ctx=ctx, error=e)

    async def invoke_react(self, cmd, ctx):
        if not cmd._buckets.valid:
            return True

        if not (await cmd.can_run(ctx)):
            return False

        bucket = cmd._buckets.get_bucket(ctx)
        retry_after = bucket.update_rate_limit()
        if retry_after:
            return False
        return True


class MusicEntry:
    def __init__(self, ctx, query):
        self.requester = ctx.author
        self.channel = ctx.channel
        self.query = query
        self.ctx = ctx


class Music(commands.Cog):
    """A robust, easy to use Music Player with reaction controls.
    Play songs with an easy to use controller and fast, reliable playback.
    Supports YouTube playlists (First 25 songs)."""

    def __init__(self, bot):
        self.bot = bot
        self.players = {}

    async def __local_check(self, ctx):
        """A check which applies to all commands in Music."""
        if ctx.invoked_with == 'help':
            return True
        if not ctx.guild:
            await ctx.send('Music commands can not be used in DMs.')
            return False
        return True

    def get_player(self, ctx):
        try:
            player = self.players[ctx.guild.id]
        except KeyError:
            player = MusicPlayer(self.bot, ctx)
            self.players[ctx.guild.id] = player

        return player

    @commands.command(name='connect', aliases=['summon', 'join', 'move'])
    @commands.cooldown(6, 60, commands.BucketType.guild)
    async def voice_connect(self, ctx, *, channel: discord.VoiceChannel=None):
        """Summon the bot to a voice channel.
        This command handles both initial joining and moving.
        Parameters
        ------------
        channel: [Optional]
            The channel to join. If left empty, attempt to join the channel you currently in."""
        channel = getattr(ctx.author.voice, 'channel', channel)
        vc = ctx.guild.voice_client

        if not channel:
            return await ctx.send('No channel to join. Please either specify a valid channel or join one.')

        if not vc:
            try:
                await channel.connect(timeout=10)
            except asyncio.TimeoutError:
                return await ctx.send('Unable to connect to the voice channel at this time. Please try again.')
            await ctx.send(f'Connected to: **{channel}**', delete_after=15)
        else:
            if channel == vc.channel:
                return
            try:
                await vc.move_to(channel)
            except Exception:
                return await ctx.send('Unable to move this channel. Perhaps missing permissions?')
            await ctx.send(f'Moved to: **{channel}**', delete_after=15)

    @commands.command(name='play')
    @commands.cooldown(30, 30, commands.BucketType.guild)
    async def play_song(self, ctx, *, query: str):
        """Add a song to the queue.
        Parameters
        ------------
        query: [Required]
            The song you wish to play. Could also be a valid URL e.g (Youtube)"""
        try:
            await ctx.message.delete()
        except discord.HTTPException:
            pass

        vc = ctx.guild.voice_client

        if vc is None:
            await ctx.invoke(self.voice_connect)
            if not ctx.guild.voice_client:
                return
        else:
            if ctx.author not in vc.channel.members:
                return await ctx.send(f'You must be in **{vc.channel}** to request songs.', delete_after=30)

        player = self.get_player(ctx)

        try:
            query = re.match(r'%3C(.*)%3E', query).group(1)
        except (IndexError, AttributeError):
            pass

        if not player.dj:
            player.dj = ctx.author
            await ctx.send(f'{ctx.author.mention} is the session DJ. Admins can change this.', delete_after=29)

        entry = MusicEntry(ctx, query)
        async with ctx.typing():
            self.bot.loop.create_task(YTDLSource.from_url(entry, loop=self.bot.loop, player=player))

        #  self.bot._counter_songs += 1

    @commands.command(name='stream')
    @commands.cooldown(30, 30, commands.BucketType.guild)
    async def stream_song(self, ctx, *, query: str):
        """Stream a song directly from youtube of provided url."""
        try:
            await ctx.message.delete()
        except discord.HTTPException:
            pass

        vc = ctx.guild.voice_client

        if vc is None:
            await ctx.invoke(self.voice_connect)
            if not ctx.guild.voice_client:
                return
        else:
            if ctx.author not in vc.channel.members:
                return await ctx.send(f'You must be in **{vc.channel}** to request songs.', delete_after=30)
        player = self.get_player(ctx)

        if not player.dj:
            player.dj = ctx.author
            await ctx.send(f'{ctx.author.mention} is the session DJ. Admins can change this.', delete_after=29)

        entry = MusicEntry(ctx, query)
        async with ctx.typing():
            self.bot.loop.create_task(YTDLSource.from_url(entry, loop=self.bot.loop, stream=True, player=player))


    @commands.command(name='stop')
    @commands.cooldown(4, 120, commands.BucketType.guild)
    async def stop_player(self, ctx):
        """Stops the player and clears the queue."""
        vc = ctx.guild.voice_client
        if ctx.author not in vc.channel.members:
            return
        player = self.get_player(ctx)

        player.killing = True

        if ctx.author.guild_permissions.manage_guild:
            pass
        elif player.dj:
            if player.dj.id == ctx.author.id:
                pass
        elif not ctx.author.id == self.bot.appinfo.owner.id:
            pass
        elif ctx.author.id != ctx.guild.me.id:
            player.killing = False
            return

        if vc is None:
            try:
                return await ctx.voice_client.disconnect(force=True)
            except Exception:
                pass

        inact = player.inactive_task

        vc.stop()

        await asyncio.sleep(1)

        try:
            await player.now_playing.delete()
        except (discord.HTTPException, AttributeError):
            pass

        try:
            player.player_task.cancel()
            del self.players[ctx.guild.id]
        except Exception as e:
            return print(e)

        await vc.disconnect()
        await ctx.send('Disconnected from voice and cleared your queue. Goodbye!', delete_after=15)

        try:
            inact.cancel()
        except Exception as e:
            print(e)
        try:
            await ctx.message.delete()
        except discord.HTTPException:
            pass

    @commands.command(name='pause')
    @commands.cooldown(5, 60, commands.BucketType.user)
    async def pause_song(self, ctx):
        """Pause the currently playing song."""
        vc = ctx.guild.voice_client
        if ctx.author not in vc.channel.members:
            return

        if vc.is_paused():
            return await ctx.send('I am already paused.', delete_after=20)

        if vc is None or not vc.is_playing():
            return await ctx.send('I am not currently playing anything.', delete_after=20)

        vc.pause()
        player = self.get_player(ctx)

        player.paused_msg = await ctx.send(f'{ctx.author.mention} has paused the song.')
        await asyncio.sleep(3)
        try:
            await ctx.message.delete()
        except discord.HTTPException:
            pass

    @commands.command(name='resume')
    async def resume_song(self, ctx):
        """Resume a song if it is currently paused."""
        vc = ctx.guild.voice_client
        if ctx.author not in vc.channel.members:
            return

        if vc is None or not vc.is_connected():
            return await ctx.send('I am not currently playing anything.', delete_after=20)

        if vc.is_paused():
            vc.resume()
            player = self.get_player(ctx)

            await player.paused_msg.edit(content=f'{ctx.author.mention} has resumed the song.', delete_after=15)
        await asyncio.sleep(3)
        try:
            await ctx.message.delete()
        except discord.HTTPException:
            pass

    @commands.command(name='skip')
    @commands.cooldown(5, 60, commands.BucketType.user)
    async def skip_song(self, ctx):
        """Skip the current song."""
        vc = ctx.guild.voice_client
        if ctx.author not in vc.channel.members:
            return

        if vc is None or not vc.is_connected():
            return await ctx.send('I am not currently playing anything.', delete_after=20)

        if ctx.author.guild_permissions.manage_guild:
            vc.stop()
            return await ctx.send(f'**{ctx.author.mention} has skipped the song as an admin.**', delete_after=15)

        player = self.get_player(ctx)
        if player.dj:
            if player.dj.id == ctx.author.id:
                vc.stop()
                return await ctx.send(f'**{ctx.author.mention} has skipped the song as the DJ.**', delete_after=15)

        vcheck = await self.vote_check(ctx, 'skip', player.skips)

        if vcheck:
            vc.stop()
            return await ctx.send('**Vote to skip has passed...** Skipping the song!', delete_after=10)
        await asyncio.sleep(3)
        try:
            await ctx.message.delete()
        except discord.HTTPException:
            pass

    @commands.command(name='volume', aliases=['vol'])
    @commands.cooldown(5, 30, commands.BucketType.user)
    async def adjust_volume(self, ctx, *, vol: int):
        """Adjust the player volume."""


        vc = ctx.guild.voice_client
        if ctx.author not in vc.channel.members:
            return

        if not 0 < vol < 101:
            return await ctx.send('Please enter a value between 1 and 100.')

        if vc is None:
            return await ctx.send('I am not currently connected to voice.')

        player = self.get_player(ctx)
        adj = float(vol) / 100

        try:
            vc.source.volume = adj
        except AttributeError:
            pass
        finally:
            player.volume = adj
            await ctx.send(f'Changed player volume to: **{vol}%**', delete_after=7)
        await asyncio.sleep(3)
        try:
            await ctx.message.delete()
        except discord.HTTPException:
            pass

    @commands.command(name='vol_down', hidden=True)
    @commands.cooldown(7, 30, commands.BucketType.user)
    async def decrease_volume(self, ctx):
        """Turn the Volume down."""

        player = self.get_player(ctx)
        vc = ctx.guild.voice_client
        if ctx.author not in vc.channel.members:
            return

        orig = int(player.volume * 100)
        vol_in = int(math.ceil((orig - 10) / 10.0)) * 10
        vol = float(vol_in) / 100

        if vol < 0.1:
            return await ctx.send('**Minimum volume reached.**', delete_after=5)

        try:
            vc.source.volume = vol
            player.volume = vol
        except AttributeError:
            await ctx.send('**I am not currently playing anything.**')
        await asyncio.sleep(3)
        try:
            await ctx.message.delete()
        except discord.HTTPException:
            pass

    @commands.command(name='vol_up', aliases=['vup', 'up'], hidden=True)
    @commands.cooldown(7, 30, commands.BucketType.user)
    async def increase_volume(self, ctx):
        """Turn the Volume Up!"""

        player = self.get_player(ctx)
        vc = ctx.guild.voice_client
        if ctx.author not in vc.channel.members:
            return

        orig = int(player.volume * 100)
        vol_in = int(math.ceil((orig + 10) / 10.0)) * 10
        vol = float(vol_in) / 100

        if vol > 1.0:
            return await ctx.send('**Max volume reached.**', delete_after=5)

        try:
            vc.source.volume = vol
            player.volume = vol
        except AttributeError:
            await ctx.send('**I am not currently playing anything.**')
        await asyncio.sleep(3)
        try:
            await ctx.message.delete()
        except discord.HTTPException:
            pass

    @commands.command(name='shuffle', aliases=['mix'])
    @commands.cooldown(3, 120, commands.BucketType.user)
    async def shuffle_song(self, ctx):
        """Shuffle all songs in your Queue."""

        vc = ctx.guild.voice_client
        if ctx.author not in vc.channel.members:
            return
        player = self.get_player(ctx)

        if vc is None:
            return await ctx.send('**I am not currently playing anything.**', delete_after=20)

        elif player.queue.qsize() <= 2:
            return await ctx.send('**Please add more songs to the Queue before shuffling.**', delete_after=15)

        elif ctx.author.guild_permissions.manage_guild:
            await self.do_shuffle(ctx, player)
            return await ctx.send(f'**{ctx.author.mention} has shuffled the playlist as an admin.**', delete_after=20)

        elif player.dj:
            if player.dj.id == ctx.author.id:
                await self.do_shuffle(ctx, player)
                return await ctx.send(f'**{ctx.author.mention} has shuffled the playlist as the DJ.**',
                                      delete_after=20)

        vcheck = await self.vote_check(ctx, 'shuffle', player.shuffles)
        if not vcheck:
            return

        await ctx.send(f'Shuffle vote passed... **The current song will replay.**', delete_after=15)
        try:
            await self.do_shuffle(ctx, player)
        except Exception as e:
            print(e)

    async def do_shuffle(self, ctx, player):
        random.shuffle(player.queue._queue)

        await ctx.invoke(self._now_playing)

    @commands.command(name='repeat', aliases=['replay'])
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def repeat_song(self, ctx):
        """Repeat/Replay the current song."""
        vc = ctx.guild.voice_client
        if ctx.author not in vc.channel.members:
            return

        if vc is None:
            return await ctx.send('**I am not currently playing anything.**', delete_after=15)

        player = self.get_player(ctx)
        if ctx.author.guild_permissions.manage_guild:
            try:
                await self.do_repeat(ctx, player)
            except Exception as e:
                print(e)
            return await ctx.send(f'**{ctx.author.mention} has repeated the song as an admin.**', delete_after=15)

        elif player.dj:
            if player.dj.id == ctx.author.id:
                try:
                    await self.do_repeat(ctx, player)
                except Exception as e:
                    print(e)
                return await ctx.send(f'**{ctx.author.mention} has repeated the song as the DJ.**', delete_after=15)

        vcheck = await self.vote_check(ctx, 'repeat', player.repeats)

        if not vcheck:
            return

        await ctx.send(f'Repeat vote passed... **The current song will replay.**', delete_after=15)
        try:
            await self.do_repeat(ctx, player)
        except Exception as e:
            print(e)

    async def do_repeat(self, ctx, player):
        player.shuffling = True

        data = player.held.data
        data['requester'] = ctx.author
        data['channel'] = ctx.channel

        source = await MusicSource.from_filename(data=data, filename=player.held.filename,
                                                 volume=player.volume)

        if not player.queue.empty():
            player.queue._queue.appendleft(source)
        else:
            await player.queue.put(source)

        if ctx.guild.voice_client.is_playing():
            await ctx.invoke(self._now_playing)

        player.shuffling = False
        await asyncio.sleep(3)
        try:
            await ctx.message.delete()
        except discord.HTTPException:
            pass

    @commands.command(name='nowplaying', aliases=['playing', 'current', 'currentsong', 'np'])
    @commands.cooldown(3, 30, commands.BucketType.guild)
    async def _now_playing(self, ctx):
        """Display the current song, and spawn the reaction controller."""
        vc = ctx.guild.voice_client

        if vc is None:
            return await ctx.send('I am not currently connected to voice.')

        player = self.get_player(ctx)

        if not player.entry:
            return

        if ctx.channel.id != player.entry.channel.id:
            return await ctx.send(f'The player is currently in {player.entry.channel.mention}.'
                                  f' Please retry the command there.')

        await player.playing_controller(player.entry)
        await asyncio.sleep(3)
        try:
            await ctx.message.delete()
        except discord.HTTPException:
            pass

    @commands.command(name='queue', aliases=['q'])
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def player_queue(self, ctx):
        """Display the current Queue of songs."""
        vc = ctx.guild.voice_client

        if vc is None:
            return await ctx.send('**I am not currently playing anything.**', delete_after=10)

        player = self.get_player(ctx)

        if player.queue.qsize() <= 0:
            return await ctx.send(f'```css\n[No songs in the Queue.]\n```', delete_after=10)

        entries = [x.title for x in player.queue._queue]
        page = SimplePaginator(title='Playlist',
                               ctx=ctx,
                               bot=self.bot,
                               colour=0xDB7093,
                               entries=entries,
                               prepend=' - `',
                               append='`',
                               inner='**+**')
        await page.embed_creator()

    async def vote_check(self, ctx, name, votes):
        vc = ctx.guild.voice_client

        req = math.ceil((len(vc.channel.members) - 1) / 2.5)

        if ctx.author.id in votes:
            need = req - len(votes)
            await ctx.send(f'{ctx.author.mention} you have already voted to {name}. **{need}** more votes required.',
                           delete_after=15)
            return False

        votes.add(ctx.author.id)

        if len(votes) >= req:
            votes.clear()
            return True

        need = req - len(votes)
        await ctx.send(f'{ctx.author.mention} has voted to {name}. **{need}** more votes required.',
                       delete_after=30)
        return False
        await asyncio.sleep(3)
        try:
            await ctx.message.delete()
        except discord.HTTPException:
            pass

    @commands.command(name='fstop', hidden=True)
    async def force_stop(self, ctx):
        errors = []
        player = self.get_player(ctx)

        player.killing = True

        if ctx.author.guild_permissions.manage_guild:
            pass
        elif player.dj:
            if player.dj.id == ctx.author.id:
                pass
        elif ctx.author == ctx.guild.me:
            pass
        elif not ctx.author.id == self.bot.appinfo.owner.id:
            player.killing = False
            return

        try:
            await player.now_playing.delete()
        except (discord.HTTPException, AttributeError):
            pass

        if ctx.guild.id not in self.players:
            try:
                return await ctx.voice_client.disconnect(force=True)
            except Exception as e:
                errors.append(e)

        try:
            await ctx.voice_client.disconnect(force=True)
        except Exception as e:
            errors.append(e)

        try:
            del self.players[ctx.guild.id]
        except Exception as e:
            errors.append(e)

        try:
            player.player_task.cancel()
            player.inactive_task.cancel()
        except Exception as e:
            errors.append(e)

        await asyncio.sleep(3)
        try:
            await ctx.message.delete()
        except discord.HTTPException:
            pass

    @commands.group(name='dj', invoke_without_command=True)
    async def _dj(self, ctx):
        """*Commands related to the management of the DJ.*
        `dj` -
            Display the current DJ.
        `dj swap <member[Optional]>` -
            Swap/Change the current DJ.
        """
        player = self.get_player(ctx)

        if not player.dj:
            return

        await ctx.send(f'Current DJ is: **{player.dj}**', delete_after=20)

    @_dj.command(name='change', aliases=['swap'])
    @has_permissions_or_dj(manage_server=True)
    @commands.cooldown(1, 120, commands.BucketType.guild)
    async def swap_dj(self, ctx, *, member: discord.Member = None):
        """Change/Swap the DJ.
         This command requires [manage_server] permissions.
         If no member is provided the invoker becomes the DJ.
         Parameters
         ------------
         member: [Optional]
            The new DJ. Could be None to make it yourself."""
        player = self.get_player(ctx)
        orig = player.dj

        if not member:
            player.dj = ctx.author
        else:
            player.dj = member

        await ctx.send(f'{orig.mention} has been removed from the DJ role... The new DJ is: {player.dj.mention}',
                       delete_after=45)

    @commands.command(name='lyrics')
    @commands.cooldown(10, 30, commands.BucketType.user)
    async def get_lyrics(self, ctx, *, query=None):
        """Get lyrics of provided song or song you're listening on spotify or in voice channel.\nIf no query is provided then it tries to search lyrics of now playing song on spotify or in voice channel\n**Note:** For getting lyrics of spotify song you listening to, you must have spotify integrated with your discord account."""
        if query is None:
            try:
                player = self.get_player(ctx)
                if ctx.guild.voice_client is None or not ctx.guild.voice_client.is_playing():
                    try:
                        if ctx.author.activity.type.value == 2:
                            query = ctx.author.activity.title + " " + ctx.author.activity.artist.split(";")[0]
                    except:
                        pass
                else:
                    query = player.entry.title
            except:
                await ctx.send("Unable to auto detect now playing song. Please provide query to find its lyrics.")

        await ctx.trigger_typing()
        genius = Genius(ctx, query)
        await genius.show_song_lyrics()


def setup(bot):
    bot.add_cog(Music(bot))
