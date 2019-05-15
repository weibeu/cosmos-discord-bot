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
        self.rewards = self.__fetch_rewards(raw_levels.get("rewards", list()))

    @staticmethod
    def __fetch_rewards(raw_rewards):
        return {raw_reward["level"]: LevelReward(**raw_reward) for raw_reward in raw_rewards}

    async def set_rewards(self, level, roles, points=0):
        reward = LevelReward(**{
            "level": level,
            roles: roles or list(),
            points: points,
        })

        self.rewards.update({reward.level: reward})

        await self.__profile.collection.update_one(self.__profile.document_filter, {"$addToSet": {
            "levels.rewards": reward.document
        }})

    async def give_rewards(self, profile):
        reward = self.rewards.get(profile.level)
        if not reward:
            return

        profile.give_points(reward.points)

        for role_id in reward.roles:
            role = self.__profile.guild.get_role(role_id)
            await profile.member.add_roles(role, reason=f"Level {profile.level} reward.")
