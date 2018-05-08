import motor.motor_asyncio
import discord
from json import load
from cogs.utils import util
def get_config():
    with open("settings/config.json") as config_file:
        config = load(config_file)
        return config
motor_client = motor.motor_asyncio.AsyncIOMotorClient(get_config()["MONGOHQ_URL"])

async def count_role(col):
    return await col.find({'_id': 'role-shop'}).count()

async def count_points(col):
    return await col.find({'_id': 'members'}).count()

async def count_user_roles(col):
    return await col.find({'_id': 'members'}).count()

async def count_settings(col):
    return await col.find({'_id': 'settings'}).count()

async def count_tag_box(col):
    return await col.find({'_id': 'tag-box'}).count()

async def insert(col, doc):
    await col.insert_one(doc)

async def get_role_shop_dict(ctx):
    guild = motor_client.guilds[str(ctx.guild.id)]
    r = await guild.find_one({'_id': 'role-shop'})
    if r is None:
        return {}
    else:
        r.pop("_id")
        return r

async def get_role_shop_buy_dict(ctx):
    guild = motor_client.guilds[str(ctx.guild.id)]
    r = await guild.find_one({'_id': 'role-shop'})
    try:
        r.pop("_id")
    except:
        return {}
    roles = {}
    p_r = await get_user_roles_purchased_list(ctx)
    for i in r:
        if i not in p_r:
            role = discord.utils.get(ctx.guild.roles, id=int(i))
            roles[i] = "\t|\t__**"+role.name+"**__\n\n\t\t\t\t`POINTS:`  **"+r[i]+"**\n"+"\t"*21+";"
    return roles

async def get_user_roles_equipped_list(ctx):
    guild = motor_client.guilds[str(ctx.guild.id)]
    d = await guild.find_one({'_id': 'members'})
    l = []
    try:
        d.pop("_id")
        roles = d[str(ctx.author.id)]["roles-rs"]
    except KeyError:
        return []
    for role in roles:
        if roles[role]:
            l.append(role)
    return l

async def get_user_roles_purchased_list(ctx):
    guild = motor_client.guilds[str(ctx.guild.id)]
    d = await guild.find_one({'_id': 'members'})
    try:
        d.pop("_id")
        return d[str(ctx.author.id)]["roles-rs"].keys()
    except KeyError:
        return []

async def get_user_roles_unequipped_list(ctx):
    p_l = await get_user_roles_purchased_list(ctx)
    e_l =await get_user_roles_equipped_list(ctx)
    ue_l = []
    for p in p_l:
        if p not in e_l:
            ue_l.append(p)
    return ue_l

async def get_role_shop_list(ctx):
    """Returns a list in particluar format of roles in role shop."""
    guild = motor_client.guilds[str(ctx.guild.id)]
    r = await guild.find_one({'_id': 'role-shop'})
    r.pop("_id")
    roles = []
    for i in r:
        role = discord.utils.get(ctx.guild.roles, id=int(i))
        roles.append("\t|\t__**"+role.name+"**__\n\n\t\t\t\t`POINTS:`  **"+r[i]+"**\n"+"\t"*16+";")
    return roles

async def get_role_shop_embed(ctx):
    """Returns discord.Embed() class which can be sent through send(embed=embed)"""
    guild = motor_client.guilds[str(ctx.guild.id)]
    r = await guild.find_one({'_id': 'role-shop'})
    r.pop("_id")
    embed = discord.Embed(title="Roles - Role Shop")
    embed.color = int(util.get_random_color(), 16)
    embed.description = "List of roles, followed by points required to purchased them.```"
    count = 1
    for i in r:
        role = discord.utils.get(ctx.guild.roles, id=int(i))
        embed.description += "["+str(count)+"]\t> "+role.name+"\n\t\t\tPOINTS:  "+r[i]+"\n\n"
        count+=1
    embed.description += "```"
    return embed

async def get_purchased_roles_embed(ctx):
    """Returns discord.Embed() class which can be sent through send(embed=embed)"""
    p_r = await get_user_roles_purchased_list(ctx)
    guild = motor_client.guilds[str(ctx.guild.id)]
    r = await guild.find_one({'_id': 'role-shop'})
    r.pop("_id")
    embed = discord.Embed(title="Roles - Role Shop")
    embed.color = int(util.get_random_color(), 16)
    embed.description = "List of roles, followed by points required to purchased them.```"
    count = 1
    for i in r:
        if i in p_r:
            role = discord.utils.get(ctx.guild.roles, id=int(i))
            embed.description += "["+str(count)+"]\t> "+role.name+"\n\t\t\tPOINTS:  "+r[i]+"\n\n"
            count+=1
    embed.description += "```"
    return embed

async def get_unequipped_roles_embed(ctx):
    """Returns discord.Embed() class which can be sent through send(embed=embed)"""
    e_r = await get_user_roles_equipped_list(ctx)
    guild = motor_client.guilds[str(ctx.guild.id)]
    r = await get_user_roles_purchased_list(ctx)
    roles = await guild.find_one({'_id': 'role-shop'})
    embed = discord.Embed(title="Roles - Role Shop")
    embed.color = int(util.get_random_color(), 16)
    embed.description = "List of roles, followed by points required to purchased them.```"
    count = 1
    for i in r:
        if i not in e_r:
            role = discord.utils.get(ctx.guild.roles, id=int(i))
            embed.description += "["+str(count)+"]\t> "+role.name+"\n\t\t\tPOINTS:  "+roles[i]+"\n\n"
            count+=1
    embed.description += "```"
    return embed

async def get_equipped_roles_embed(ctx):
    """Returns discord.Embed() class which can be sent through send(embed=embed)"""
    e_r = await get_user_roles_equipped_list(ctx)
    guild = motor_client.guilds[str(ctx.guild.id)]
    roles = await guild.find_one({'_id': 'role-shop'})
    embed = discord.Embed(title="Roles - Role Shop")
    embed.color = int(util.get_random_color(), 16)
    embed.description = "List of roles, followed by points required to purchased them.```"
    count = 1
    for i in e_r:
        role = discord.utils.get(ctx.guild.roles, id=int(i))
        embed.description += "["+str(count)+"]\t> "+role.name+"\n\t\t\tPOINTS:  "+roles[i]+"\n\n"
        count+=1
    embed.description += "```"
    return embed

async def get_role_shop_buy_embed(ctx):
    """Returns embed for buy menu"""
    p_r = await get_user_roles_purchased_list(ctx)
    guild = motor_client.guilds[str(ctx.guild.id)]
    r = await guild.find_one({'_id': 'role-shop'})
    r.pop("_id")
    embed = discord.Embed(title="Roles - Role Shop")
    embed.color = int(util.get_random_color(), 16)
    embed.description = "List of roles, followed by points required to purchased them.```"
    count = 1
    for i in r:
        if i not in p_r:
            role = discord.utils.get(ctx.guild.roles, id=int(i))
            embed.description += "["+str(count)+"]\t> "+role.name+"\n\t\t\tPOINTS:  "+r[i]+"\n\n"
            count+=1
    embed.description += "```"
    return embed

async def role_shop_create(ctx, role, points):
    guild = motor_client.guilds[str(ctx.guild.id)]
    if await count_role(guild)==0:
        await insert(guild, {'_id': 'role-shop'})
    await guild.update_one({'_id': 'role-shop'}, {'$set': {str(role.id): points}})

async def remove_role(ctx, role_id, points):
    guild = motor_client.guilds[str(ctx.guild.id)]
    await guild.update_one({'_id': 'role-shop'}, {'$unset': {str(role_id): str(points)}})

async def give_points(guild_id, user_id, points):
    guild = motor_client.guilds[str(guild_id)]
    if await count_points(guild)==0:
        await insert(guild, {'_id': 'members'})
    await guild.update({'_id': 'members'}, {'$inc': {str(user_id)+".points": points}})

async def get_points(guild_id, user_id):
    """Returns points of user_id in string"""
    guild = motor_client.guilds[str(guild_id)]
    p = await guild.find_one({'_id': 'members'})
    return str(p[str(user_id)]["points"])

async def get_all_points(guild_id):
    guild = motor_client.guilds[str(guild_id)]
    points = {}
    p = await guild.find_one({'_id': 'members'})
    p.pop("_id")
    for user_id in p:
        try:
            points[p[user_id]["points"]] = user_id
        except:
            pass
    return points

async def give_user_role(ctx, role_id):
    guild = motor_client.guilds[str(ctx.guild.id)]
    if await count_user_roles(guild)==0:
        await insert(guild, {'_id': 'members'})
    await guild.update_one({'_id': 'members'}, {'$set': {str(ctx.author.id)+".roles-rs."+str(role_id): False}})

async def equip_user_role(ctx, role_id):
    guild = motor_client.guilds[str(ctx.guild.id)]
    if await count_user_roles(guild)==0:
        await insert(guild, {'_id': 'members'})
    await guild.update_one({'_id': 'members'}, {'$set': {str(ctx.author.id)+".roles-rs."+str(role_id): True}})

async def unequip_user_role(ctx, role_id):
    guild = motor_client.guilds[str(ctx.guild.id)]
    if await count_user_roles(guild)==0:
        await insert(guild, {'_id': 'members'})
    await guild.update_one({'_id': 'members'}, {'$set': {str(ctx.author.id)+".roles-rs."+str(role_id): False}})

async def buy_role(ctx, role_id):
    guild = motor_client.guilds[str(ctx.guild.id)]
    roles = await get_role_shop_dict(ctx)
    point = int(roles[str(role_id)])
    await guild.update({'_id': 'members'}, {'$inc': {str(ctx.author.id)+".points": -point}})
    await give_user_role(ctx, role_id) #finally adding role to user purchased list

async def setup_reactor(ctx, emojis):
    guild = motor_client.guilds[str(ctx.guild.id)]
    if await count_settings(guild)==0:
        await insert(guild, {'_id': 'settings'})
    await guild.update_one({'_id': 'settings'}, {'$set': {"reactor."+str(ctx.channel.id)+".is_on": False}})
    await guild.update_one({'_id': 'settings'}, {'$set': {"reactor."+str(ctx.channel.id)+".emojis": emojis}})

async def get_reactor_settings(guilds):
    r_s = {}
    for g in guilds:
        guild = motor_client.guilds[str(g.id)]
        s = await guild.find_one({'_id': 'settings'})
        if s is None:
            pass
        else:
            try:
                r_s[str(g.id)] = s["reactor"]
            except:
                continue
    return r_s

async def toggle_reactor_on(ctx):
    guild = motor_client.guilds[str(ctx.guild.id)]
    if await count_settings(guild)==0:
        await insert(guild, {'_id': 'settings'})
    await guild.update_one({'_id': 'settings'}, {'$set': {"reactor."+str(ctx.channel.id)+".is_on": True}})

async def toggle_reactor_off(ctx):
    guild = motor_client.guilds[str(ctx.guild.id)]
    if await count_settings(guild)==0:
        await insert(guild, {'_id': 'settings'})
    await guild.update_one({'_id': 'settings'}, {'$set': {"reactor."+str(ctx.channel.id)+".is_on": False}})

async def dump_nick(guild_id, user_id, nick):
    guild = motor_client.guilds[str(guild_id)]
    if await count_points(guild) == 0:
        await insert(guild, {'_id': 'members'})
    await guild.update({'_id': 'members'}, {'$addToSet': {str(user_id)+".nicks": nick}})

async def get_nicks(guild_id, user_id):
    guild = motor_client.guilds[str(guild_id)]
    d = await guild.find_one({'_id': 'members'})
    try:
        d.pop("_id")
        return d[str(user_id)]["nicks"]
    except:
        return []

async def dump_username(guild_id, user_id, username):
    guild = motor_client.guilds[str(guild_id)]
    if await count_points(guild) == 0:
        await insert(guild, {'_id': 'members'})
    await guild.update({'_id': 'members'}, {'$addToSet': {str(user_id)+".usernames": username}})

async def get_usernames(guild_id, user_id):
    guild = motor_client.guilds[str(guild_id)]
    d = await guild.find_one({'_id': 'members'})
    try:
        d.pop("_id")
        return d[str(user_id)]["usernames"]
    except:
        return []

async def shutup_bot(guild_id, channel_id):
    guild = motor_client.guilds[str(guild_id)]
    if await count_settings(guild)==0:
        await insert(guild, {'_id': 'settings'})
    await guild.update_one({'_id': 'settings'}, {'$addToSet': {"shutup-channels": str(channel_id)}})

async def unshutup_bot(guild_id, channel_id):
    guild = motor_client.guilds[str(guild_id)]
    if await count_settings(guild)==0:
        await insert(guild, {'_id': 'settings'})
    await guild.update_one({'_id': 'settings'}, {'$unset': {"shutup-channels": str(channel_id)}})

async def get_shutup_channels(guild_id):
    guild = motor_client.guilds[str(guild_id)]
    d = await guild.find_one({'_id': 'settings'})
    try:
        d.pop("_id")
        return d["shutup-channels"]
    except:
        return []

'''async def leaderboard_points(ctx):
    """Returns guild points leaderboard dict."""
    guild = motor_client.guilds[str(ctx.guild.id)]
    p = await guild.find_one({'_id': 'members'})
    author_points = str(p[str(ctx.author.id)]["points"])
    for '''

async def setup_omjcd(guild_id, role_id, cooldown):
    guild = motor_client.guilds[str(guild_id)]
    if await count_settings(guild)==0:
        await insert(guild, {'_id': 'settings'})
    await guild.update_one({'_id': 'settings'}, {'$set': {"omjcd.enabled": False}})
    await guild.update_one({'_id': 'settings'}, {'$set': {"omjcd.role": str(role_id)}})
    await guild.update_one({'_id': 'settings'}, {'$set': {"omjcd.cooldown": str(cooldown)}})

async def get_omjcd_setting(guild_id):
    guild = motor_client.guilds[str(guild_id)]
    s = await guild.find_one({'_id': 'settings'})
    try:
        return s["omjcd"]
    except:
        return {}

async def get_omjcd_settings(guilds):
    settings = {}
    for g in guilds:
        guild = motor_client.guilds[str(g.id)]
        s = await guild.find_one({'_id': 'settings'})
        if s is None:
            pass
        else:
            try:
                settings[str(g.id)] = s["omjcd"]
            except:
                continue
    return settings

async def enable_omjcd(ctx):
    setting = await get_omjcd_setting(ctx.guild.id)
    if setting == {}:
        await ctx.send("OMJCD setup not completed yet")
    else:
        guild = motor_client.guilds[str(ctx.guild.id)]
        await guild.update_one({'_id': 'settings'}, {'$set': {"omjcd.enabled": True}})

async def disable_omjcd(ctx):
    setting = await get_omjcd_setting(ctx.guild.id)
    if setting == {}:
        await ctx.send("OMJCD setup not completed yet")
    else:
        guild = motor_client.guilds[str(ctx.guild.id)]
        await guild.update_one({'_id': 'settings'}, {'$set': {"omjcd.enabled": False}})

async def setup_sc(guild_id, msg_channel_id, log_channel_id):
    guild = motor_client.guilds[str(guild_id)]
    if await count_settings(guild)==0:
        await insert(guild, {'_id': 'settings'})
    await guild.update_one({'_id': 'settings'}, {'$set': {"sc.enabled": True}})
    await guild.update_one({'_id': 'settings'}, {'$set': {"sc.message_channel": str(msg_channel_id)}})
    await guild.update_one({'_id': 'settings'}, {'$set': {"sc.log_channel": str(log_channel_id)}})

async def get_sc_settings(guilds):
    settings = {}
    for g in guilds:
        guild = motor_client.guilds[str(g.id)]
        s = await guild.find_one({'_id': 'settings'})
        if s is None:
            pass
        else:
            try:
                settings[str(g.id)] = s["sc"]
            except:
                continue
    return settings

async def enable_sc(ctx):
    setting = await get_omjcd_setting(ctx.guild.id)
    if setting == {}:
        await ctx.send("SC setup not completed yet")
    else:
        guild = motor_client.guilds[str(ctx.guild.id)]
        await guild.update_one({'_id': 'settings'}, {'$set': {"sc.enabled": True}})

async def disable_sc(ctx):
    setting = await get_omjcd_setting(ctx.guild.id)
    if setting == {}:
        await ctx.send("SC setup not completed yet")
    else:
        guild = motor_client.guilds[str(ctx.guild.id)]
        await guild.update_one({'_id': 'settings'}, {'$set': {"sc.enabled": False}})

async def create_tag(guild_id, user_id, tag_name, content):
    guild = motor_client.guilds[str(guild_id)]
    if await count_points(guild)==0:
        await insert(guild, {'_id': 'members'})
    await guild.update({'_id': 'members'}, {'$set': {str(user_id)+".tags."+tag_name: content}})

async def get_tag(guild_id, user_id, tag_name):
    guild = motor_client.guilds[str(guild_id)]
    p = await guild.find_one({'_id': 'members'})
    try:
        return p[str(user_id)]["tags"][tag_name]
    except:
        return None

async def get_tags(guild_id, user_id):
    guild = motor_client.guilds[str(guild_id)]
    p = await guild.find_one({'_id': 'members'})
    try:
        return p[str(user_id)]["tags"]
    except:
        return None

async def remove_tag(guild_id, user_id, tag_name, content):
    guild = motor_client.guilds[str(guild_id)]
    await guild.update_one({'_id': 'members'}, {'$unset': {str(user_id)+".tags."+tag_name: content}})

async def create_tag_box(guild_id, tag_name, content):
    guild = motor_client.guilds[str(guild_id)]
    if await count_tag_box(guild)==0:
        await insert(guild, {'_id': 'tag-box'})
    await guild.update({'_id': 'tag-box'}, {'$set': {tag_name: content}})

async def get_tag_box(guild_id, tag_name):
    guild = motor_client.guilds[str(guild_id)]
    p = await guild.find_one({'_id': 'tag-box'})
    try:
        return p[tag_name]
    except:
        return None

async def get_tags_box(guild_id):
    guild = motor_client.guilds[str(guild_id)]
    p = await guild.find_one({'_id': 'tag-box'})
    try:
        p.pop('_id')
        return p
    except:
        return None

async def remove_tag_box(guild_id, tag_name, content):
    guild = motor_client.guilds[str(guild_id)]
    await guild.update_one({'_id': 'tag-box'}, {'$unset': {tag_name: content}})
