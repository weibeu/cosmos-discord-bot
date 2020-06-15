---
description: Plugin for server moderation.
---

# Moderation

## ;modlogs

Displays all of the moderation logs of specified member.

{% hint style="info" %}
All of the Timestamps are displayed in UTC.
{% endhint %}

```yaml
Usage:
;modlogs <member>
```

### ;modlogs clean

Removes and cleans all of the previous moderation logs of specified member.

```yaml
Aliases:
- purge
- clear

Usage:
;modlogs clean <member>
```

## ;warn

Issues a warning to specified member. Also notifies them automatically by direct message.

```yaml
Usage:
;warn <member> <reason>
```

## ;kick

Kicks specified member from the server. It also notifies them automatically along with the given reason.

```yaml
;kick <member> [reason]
```

## ;ban

Bans specified member from the server. It also notifies them automatically along with the given reason.

If the user is not present in the server, their discord ID can be passed as member parameter.

```yaml
Usage:
;ban <member> [reason]
```

## ;unban

Un bans user from their discord ID.

```yaml
Usage:
;unban <user_id> [reason]
```

## ;clean

Cleans and deleted last few messages sent by the bot.

```yaml
Usage:
;clean
```

## ;mute

Mutes specified member from voice and also adds the muted role. It also notifies them automatically along with the given reason.

```yaml
Usage:
;mute <member> [reason]
```

### ;mute role

Sets muted role for server which will be used to enforce restrictions on members when they're muted.  
It creates a new role to use denying sending messages to all of the text channels if not provided.

```yaml
Usage:
;mute role [role]
```

## ;unmute

Un mutes specified member from voice and removes the muted role. It also notifies them automatically.

```yaml
Usage:
;unmute <member>
```

## ;purge

Removes and purges messages which meets specified criteria. To specify any criteria, consider using its sub-commands. If this primary command is used, performs the default purge which removes last specified number of messages.

```yaml
Aliases:
- prune

Usage:
;purge [search=100]
```

### ;purge text

Removes all of the messages containing only texts, ignores files or any attachments.

```yaml
Aliases:
- text

Usage:
;purge text [search=100]
```

### ;purge embeds

Removes messages that have embeds in them. Embed messages are sent by webhooks and other bots.

```yaml
Aliases:
- embed

Usage:
;purge embeds [search=100]
```

### ;purge embeds

Removes messages that have embeds in them. Embed messages are sent by webhooks and other bots.

```yaml
Aliases:
- embed

Usage:
;purge embeds [search=100]
```

### ;purge files

Removes messages that have attachments in them.

```yaml
Aliases:
- file

Usage:
;purge files [search=100]
```

### ;purge images

Removes messages that have embeds or attachments.

```yaml
Aliases:
- image

Usage:
;purge images [search=100]
```

### ;purge all

Another alias to the primary purge command which deletes any of the messages for provided search limit.

```yaml
Aliases:
- everything

Usage:
;purge all [search=100]
```

### ;purge user

Removes all messages sent by the specified member.

```yaml
Aliases:
- member

Usage:
;purge user <user> [search=100]

Examples:
;purge user @thecosmos#7777 20
```

### ;purge contains

Removes all messages containing a substring. The substring must be at least 3 characters long.

```yaml
Aliases:
- has

Usage:
;purge contains <sub string>
```

### ;purge bot

Removes a bot user's messages and messages with their optional prefix.

```yaml
Usage:
;purge bot [prefix] [search=100]

Examples:
;purge bot ! 20
```

### ;purge emoji

Removes all messages containing custom emoji.

```yaml
Aliases:
- emojis
- emotes
- emote

Usage:
;purge emoji [search=100]
```

### ;purge reactions

Removes all reactions from messages that have them.

```yaml
Aliases:
- reaction

Usage:
;purge reactions [search=100]
```