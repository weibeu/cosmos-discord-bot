---
description: Manage important configuration and settings of server.
---

# Administrator Settings

## ;moderators

Displays list of roles and members who has been assigned as special moderators who can use all of the commands from Moderation plugin and more.

```yaml
Aliases:
- moderator
- mod
- mods

Usage:
;moderators
```

### ;moderators add

Adds any role or member as special moderators who can use commands from Moderation plugin and more.

```yaml
Usage:
;moderators add <moderator>
```

### ;moderators remove

Removes any role or member from special moderators.

```yaml
Usage:
;moderators remove <moderator>
```

## ;preset

Sets preset for commands to display certain preset message including images or files every time these commands are used.

#### Commands supporting presets:

* kick
* ban
* serverboost

```yaml
Aliases:
- presets

Usage:
;preset <command_name> <image_url> [text]
```

### ;preset serverboost

Set customized preset message for loggers when someone boosts the server.

```yaml
Aliases:
- serverboosts

Usage:
;preset serverboost <message>
```

### ;preset remove

Removes any preset if it was set for specified command.

```yaml
Aliases:
- clear
- delete

Usage:
;preset remove <command_name>
```

### ;makeprime

Command to grant prime membership to any of the servers you're administrator of.

You must already have a valid prime subscription before using this command. This same prime tier will get linked to specified server. Assumes current server if no server is explicitly specified.

```yaml
Aliases:
- claimprime
- redeemprime

Usage:
;makeprime [server]
```
