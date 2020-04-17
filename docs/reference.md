# Reference

## Reference

Cosmos bot uses modular approach for each of its functions and commands. Each of the Primary Commands are categorized into different sub-commands based on their usage. A Plugin bundles many of these commands revolving around any of the specific function. Multiple plugins forms a Galaxy.

### The Functions Hierarchy

**Galaxy** &gt; **Plugin** &gt; **Command** &gt; **Sub-Command**

#### Galaxies

* GUILD
* MODERATION
* PROFILE
* SETTING
* TOOLS

#### Plugins

* [AdministratorSettings](settings/administrator-settings.md)
* [AutoModeration](moderation/auto-moderation.md)
* [Economy](profile/economy.md)
* [CosmosPermissions](guild/cosmos-permissions.md)
* [GuildSettings](guild/guild-settings/)
* [HasteBin](tools/haste-bin.md)
* [Leaderboards](profile/leaderboards.md)
* [Levels](guild/levels.md)
* [Logger](moderation/logger.md)
* [Marriage](profile/marriage.md)
* [Moderation](moderation/moderation.md)
* [Profile](profile/profile.md)
* [ReactionRoles](guild/reaction-roles.md)
* [Reactor](guild/reactor.md)
* [RoleShop](guild/role-shop/)
* [Secret Confessions](guild/secret-confessions.md)
* [Starboard](guild/starboard.md)
* [Tags](tools/tags.md)
* [UserVerification](moderation/user-verification.md)
* [Welcome](guild/welcome/)

#### **Primary** Commands

The following table displays entire list of primary commands and their basic syntax to use. Click on the command to know more about it including their **sub-commands**.

**Default Command Prefix**

**;**

You can also mention the bot and use the same as a prefix to invoke any of the commands.  
**Example:** `@Cosmos2406 ...`

**Understanding the syntax**

All of the usages provided for each commands and sub-commands follow a certain syntax, very much similar to the way these commands will be actually used.  
Every command begins with a pre-defined [prefix](guild/guild-settings/prefix.md) which can be the default prefix, `;` or any of the custom prefixes you have set. Following with the Primary Command, optional sub-command and arguments.

**Syntax:** `<prefix><primary command> [sub-command] [argument1] ...`

* The arguments under `<argument>` are required arguments.
* The arguments under `[argument]` are optional arguments.

| Command | Short Description | Usage |
| :---: | :---: | :---: |
| [ban](https://cosmos.thecosmos.space/moderation/moderation#ban) | Bans specified member from the server. | `;ban <member> [reason]` |
| [banword](https://cosmos.thecosmos.space/moderation/auto-moderation#banword) | Blacklists or bans specified word. | `;banword [word]` |
| [bosons](https://cosmos.thecosmos.space/profile/economy#bosons) | Displays Bosons earned by you or specified member. | `;bosons [user]` |
| [confessions](guild/secret-confessions.md#confessions) | Lets you confess anonymously in specified server. | `;confess <server_id> <confession>` |
| [disable](guild/cosmos-permissions.md#disable) | Disables provided function from one or multiple channels which are specified. | `;disable <function> [channels...]` |
| [divorce](https://cosmos.thecosmos.space/profile/marriage#divorce) | Lets you divorce if you're already married to someone. | `;divorce` |
| [enable](guild/cosmos-permissions.md#enable) | Enables provided function in all of the specified channels. | `;enable <function> [channels...]` |
| [fermions](https://cosmos.thecosmos.space/profile/economy#fermions) | Displays number of Fermions you have. | `;fermions` |
| [givepoints](guild/role-shop/settings.md#givepoints) | Generate and give points to specified member. | `;givepoints <points> <member>` |
| [hastebin](https://cosmos.thecosmos.space/tools/haste-bin#hastebin) | Posts the provided content to [https://hastebin.com/](https://hastebin.com/) and displays a shareable link. | `;hastebin <content>` |
| [kick](https://cosmos.thecosmos.space/moderation/moderation#kick) | Kicks specified member from the server. | `;kick <member> [reason]` |
| [leaderboards](profile/leaderboards.md#leaderboards) | Displays top members with maximum chat experience points. | `;leaderboards` |
| [level](https://cosmos.thecosmos.space/levels#level) | Displays current level and experience points. | `;level [member]` |
| [logger](https://cosmos.thecosmos.space/moderation/logger#logger) | Displays list of loggers enabled in different channels. | `;logger` |
| [moderators](https://cosmos.thecosmos.space/settings/administrator-settings#moderators) | Displays list of roles and members who has been assigned as special moderators. | `;moderators` |
| [modlogs](https://cosmos.thecosmos.space/moderation/moderation#modlogs) | Displays all of the moderation logs of specified member. | `;modlogs <member>` |
| [mute](https://cosmos.thecosmos.space/moderation/moderation#mute) | Mutes specified member from voice and also adds the muted role. | `;mute <member> [reason]` |
| [points](https://cosmos.thecosmos.space/role-shop/points#points) | Displays Guild Points earned by you or specified member. | `;points [member]` |
| [prefix](https://cosmos.thecosmos.space/guild-settings/prefix#prefix) | Displays currently set custom prefixes. | `;prefix` |
| [preset](https://cosmos.thecosmos.space/settings/administrator-settings#preset) | Sets preset for commands to display certain preset message. | `;preset <command_name> <image_url> [text]` |
| [profile](https://cosmos.thecosmos.space/profile/profile#profile) | Displays your Cosmos Profile or of specified member. | `;profile [user]` |
| [propose](https://cosmos.thecosmos.space/profile/marriage#propose) | Lets you propose them. | `;propose <user>` |
| [reaction](https://cosmos.thecosmos.space/reaction-roles#reaction) | It contains multiple reaction based sub-commands. | `;reaction` |
| [reactor](https://cosmos.thecosmos.space/reactor#reactor) | Displays reactor settings of current or specified channel. | `;reactor [channel]` |
| [rep](https://cosmos.thecosmos.space/profile/profile#rep) | Add a reputation point to specified member. | `;rep [user]` |
| [roleshop](https://cosmos.thecosmos.space/role-shop#roleshop) | Displays all of the roles which can be purchased from role shop. | `;roleshop` |
| [starboard](https://cosmos.thecosmos.space/starboard#starboard) | Configure Starboard in server. | `;starboard <sub-command> ...` |
| [tag](https://cosmos.thecosmos.space/tools/tags#tag) | Retrieves and displays specified tag and all of its contents. | `;tag <name>` |
| [tags](https://cosmos.thecosmos.space/tools/tags#tags) | Displays list of custom tags created and owned by you. | `;tags` |
| [theme](https://cosmos.thecosmos.space/guild-settings/theme#theme) | Configure theme settings. | `;theme <sub-command> ...` |
| [triggers](https://cosmos.thecosmos.space/moderation/auto-moderation#triggers) | Displays all of the active triggers along with their actions. | `;triggers` |
| [unban](https://cosmos.thecosmos.space/moderation/moderation#unban) | Un bans user from their discord ID. | `;unban <user_id> [reason]` |
| [unmute](https://cosmos.thecosmos.space/moderation/moderation#unmute) | Un mutes specified member from voice and removes the muted role. | `;unmute <member>` |
| [verification](moderation/user-verification.md#verification) | Primary command to setup several verification methods. | `;verification` |
| [warn](https://cosmos.thecosmos.space/moderation/moderation#warn) | Issues a warning to specified member. | `;warn <member> <reason>` |
| [welcome](https://cosmos.thecosmos.space/welcome#welcome) | Manage different welcome settings of your server. | `;welcome` |

