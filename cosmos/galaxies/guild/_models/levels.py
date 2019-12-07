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
        self.text_rewards = self.__fetch_rewards(raw_levels.get("text_rewards", list()))
        self.voice_rewards = self.__fetch_rewards(raw_levels.get("voice_rewards", list()))

    @staticmethod
    def __fetch_rewards(raw_rewards):
        return {raw_reward["level"]: LevelReward(**raw_reward) for raw_reward in raw_rewards}

    async def set_rewards(self, level, roles, points=0, channel="text"):
        reward = LevelReward(**{
            "level": level,
            "roles": roles or list(),
            "points": points,
        })
        channel_filter = f"{channel}_rewards"
        rewards = self.__getattribute__(f"{channel}_rewards")

        rewards.update({reward.level: reward})

        await self.__profile.collection.update_one(
            self.__profile.document_filter, {"$pull": {f"levels.{channel_filter}": {"level": reward.level}}}
        )

        await self.__profile.collection.update_one(self.__profile.document_filter, {"$addToSet": {
            f"levels.{channel_filter}": reward.document
        }})

    def get_rewards(self, channel):
        return self.__getattribute__(f"{channel}_rewards")

    async def remove_rewards(self, level, channel="text"):
        rewards = self.get_rewards(channel)

        rewards.pop(level)

        self.__profile.collection.update_one(
            self.__profile.document_filter, {"$pull": {
                f"levels.{channel}_rewards": {"level": level}
            }}
        )

    async def give_rewards(self, profile, channel="text"):
        rewards = self.get_rewards(channel)
        reward = rewards.get(profile.level)
        if not reward:
            return

        profile.give_points(reward.points)

        for role_id in reward.roles:
            role = self.__profile.guild.get_role(role_id)
            await profile.member.add_roles(role, reason=f"{channel.title()} - Level {profile.level} reward.")
