---
description: >-
  A utility plugin to automatically add reactions to message sent in text
  channels.
---

# Reactor

## ;reactor

Displays reactor settings of current or specified channel.

```yaml
Aliases:
- reactors

Usage:
;reactor [channel]
```

### set

Setup reactor in current or specified channel using provided emotes. You can only use the emotes which     the bot can see. It enables reactors just after this setup is complete.

```yaml
Aliases:
- setup

Usage:
;reactor set [channel] [emotes...]
```

### remove

Removes any reactor set in current or specified channel.

```yaml
Aliases:
- delete

Usage:
;reactor remove [channel]
```

### enable

Enable reactor if it was set of current or specified channel.

```yaml
Aliases:
- on

Usage:
;reactor enable [channel]
```

### disable

Disable reactor from current or specified channel.

```yaml
Aliases:
- off

Usage:
;reactor disable [channel]
```

