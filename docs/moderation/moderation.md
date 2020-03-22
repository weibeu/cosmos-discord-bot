---
description: Plugin for server moderation.
---

# Moderation

## ;modlogs

Displays all of the moderation logs of specified member.

```yaml
Usage:
;modlogs <member>
```

### clean

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

## ;mute

Mutes specified member from voice and also adds the muted role. It also notifies them automatically along with the given reason.

```yaml
Usage:
;mute <member> [reason]
```

### role

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



