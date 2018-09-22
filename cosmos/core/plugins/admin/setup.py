from cosmos.core.plugins.admin.controller import Controller

def setup(bot):
    bot.add_cog(Controller(bot))