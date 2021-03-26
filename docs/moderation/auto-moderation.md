---
description: An Auto Moderation plugin based on triggers and actions.
---

# Auto Moderation

Server Administrators can create different triggers and specify various actions for it. The bot responds and performs all of the actions which were specified for this trigger when a member violates its protocol. A single trigger can have multiple actions set.

#### Available Triggers:

* `links` -- Triggers when message contains any URL or links.
* `spoilers` -- Triggers when a member sends any kind of spoiler content.
* `emoji_spam` -- Triggers when there are lots of emotes in a single message.
* `banned_words` -- Triggers when a message contains any of the banned or blacklisted words.
* `mass_mentions` -- Triggers when there are lots of mentions in a single message.
* `discord_invites` -- Triggers when a message contains invites to different discord servers.

#### Available trigger Actions:

* `delete` -- Deletes the message which invoked the trigger.
* `warn` -- Warns the member who invoked the trigger.
* `mute` -- Mutes the member who invoked the trigger by adding the muted role.
* `kick` -- Kicks the member who invoked the trigger.
* `ban` -- Bans the member who invoked the trigger.

## ;triggers

Displays all of the active triggers along with their actions.

```yaml
Aliases:
- trigger
- violation
- violations

Usage:
;triggers
```

### ;triggers create

Sets a new Auto Moderation trigger with specified actions.

```yaml
Aliases:
- set
- add

Usage:
;triggers create <trigger> [actions...]

Examples:
# Create trigger to automatically warn and delete the message for discord invites.
;triggers create discord_invites warn delete

# Trigger to automatically mute someone when they mass mention.
;triggers create mass_mentions mute
```

### ;triggers remove

Removes specified Auto Moderation trigger.

```yaml
Aliases:
- delete

Usage:
;triggers remove <trigger>
```

## ;banword

Blacklists or bans specified word. To make it work, first set `banned_words` Auto Moderation trigger.

```yaml
Aliases:
- bannedwords
- banwords

Usage:
;banword [word]
```

### ;banword clear

Removes all of the currently blacklisted or banned words.

```yaml
Aliases:
- clean
- purge

Usage:
;banword clear
```

### ;banword remove

Removes given word from the currently blacklisted or banned words.

```yaml
Aliases:
- pop
- pull

Usage:
;banword remove <word>
```

