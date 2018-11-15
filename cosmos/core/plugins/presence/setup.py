from cosmos.core.plugins.presence.presence import Presence


def setup(bot):
    bot.add_cog(Presence(bot))
