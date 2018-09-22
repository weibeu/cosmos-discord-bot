from cosmos.core.plugins.admin.controller.evaluator import Evaluator

def setup(bot):
    bot.add_cog(Evaluator(bot))
