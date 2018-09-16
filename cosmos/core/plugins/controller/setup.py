from cosmos.core.plugins.controller.controller import Controller

def setup(bot):
    bot.add_cog(Controller(bot))