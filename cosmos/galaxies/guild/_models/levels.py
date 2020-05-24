from itertools import chain


class LevelReward(object):

    def __init__(self, **kwargs):
        self.level = kwargs["level"]
        self.roles = kwargs["roles"]
        self.points = kwargs.get("points", 0)

    @property
    def document(self):
        _document = {
            "level": self.level,
            "roles": self.roles,
        }
        if self.points:
            _document["points"] = self.points
        return _document


class Levels(object):

    def __init__(self, guild_profile, **kwargs):
        self.__profile = guild_profile
        raw_levels = kwargs.get("levels", dict())
        raw_rewards = raw_levels.get("rewards", dict())
        self.text_rewards = self.__fetch_rewards(raw_rewards.get("text", list()))
        self.voice_rewards = self.__fetch_rewards(raw_rewards.get("voice", list()))
        self.stack_text_roles = raw_rewards.get("stack_text_roles", True)
        self.stack_voice_roles = raw_rewards.get("stack_voice_roles", True)

    @staticmethod
    def __fetch_rewards(raw_rewards):
        return {raw_reward["level"]: LevelReward(**raw_reward) for raw_reward in raw_rewards}

    async def set_rewards(self, level, roles, points=0, channel="text"):
        reward = LevelReward(**{
            "level": level,
            "roles": roles or list(),
            "points": points,
        })
        rewards = self.get_rewards(channel)

        rewards.update({reward.level: reward})

        await self.__profile.collection.update_one(
            self.__profile.document_filter, {"$pull": {f"levels.rewards.{channel}": {"level": reward.level}}}
        )

        await self.__profile.collection.update_one(self.__profile.document_filter, {"$addToSet": {
            f"levels.rewards.{channel}": reward.document
        }})

    def get_rewards(self, channel):
        return self.__getattribute__(f"{channel}_rewards")

    def get_stack_meta(self, channel):
        return self.__getattribute__(f"stack_{channel}_roles")

    async def remove_rewards(self, level, channel="text"):
        rewards = self.get_rewards(channel)

        rewards.pop(level)

        self.__profile.collection.update_one(
            self.__profile.document_filter, {"$pull": {
                f"levels.rewards.{channel}": {"level": level}
            }}
        )

    async def give_rewards(self, profile, channel="text"):
        rewards = self.get_rewards(channel)
        level = profile.voice_level if channel == "voice" else profile.level
        reward = rewards.get(level)
        if not reward:
            return

        profile.give_points(reward.points)

        stack = self.get_stack_meta(channel)
        if not stack:
            roles = [self.__profile.guild.get_role(_) for _ in chain.from_iterable([
                __.roles for __ in rewards.values() if __.level < level])]
            await profile.member.remove_roles(*roles, reason=f"Unstack levelling roles.")

        roles = [self.__profile.guild.get_role(_) for _ in reward.roles] if not stack else [
            self.__profile.guild.get_role(_) for _ in
            chain.from_iterable([__.roles for __ in rewards.values() if __.level <= level])]
        await profile.member.add_roles(*roles, reason=f"{channel.title()} - Level {level} reward.")

    async def configure(self, channel, stack):
        if channel == "voice":
            self.stack_voice_roles = stack
        if channel == "text":
            self.stack_text_roles = stack

        await self.__profile.collection.update_one(self.__profile.document_filter, {"$set": {
            f"levels.rewards.stack_{channel}_roles": stack}})
