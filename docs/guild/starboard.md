---
description: A plugin which implements Starboard feature in server.
---

# Starboard

Reactions on messages when exceed specified number of stars, they are posted in a certain channel which has been set previously.

#### Valid Starboard Emotes:

* ⭐
* 🌟
* 🤩

## ;starboard

Configure Starboard in server.

### ;starboard set

Set starboard in server for specified number of stars in specified channel.

```yaml
Aliases:
- setup
- create

Usage:
;starboard set [stars] [channel]
```

### ;starboard remove

Remove starboard from server.

```yaml
Aliases:
- delete

Usage:
;starboard remove
```

