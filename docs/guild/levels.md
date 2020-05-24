---
description: >-
  A plugin to implement text or voice levelling feature in server and related
  commands.
---

# Levels

## ;level

Displays current rank, level and experience points gained in current server.

```yaml
Aliases:
- levels
- rank

Usage:
;level [member]
```

### ;level global

Displays current rank, level and experience points gained globally across all mutual servers.

```yaml
Aliases:
- cosmos
- globals

Usage:
;level global [member]
```

### ;level reward

Displays any rewards set for specified or all of the levels. Optionally pass `text` to view Text Levels rewards and `voice` for Voice Levels rewards.

**Available Options**

- `channel` -- The levelling channel to set rewards for. Can be either of `text` or `voice`. Defaults to `text`.
- `points` -- Amount of guild points to awards. Which can be used and redeemed by members in role shop.

```yaml
Aliases:
- rewards

Usage:
;level reward [channel=text] [level]
```

#### ;level reward set

Set rewards for specified Text or Voice Levels.

You can set one or multiple roles and optionally Guild Points as rewards.

```yaml
Usage:
;level reward set <level> [channel=text] [points=0] <roles...>
```

#### ;level reward remove

Remove any Text or Voice Level rewards set for specified level.

```yaml
Aliases:
- delete

Usage:
;level reward remove <level> [channel=text]
```


### ;level resetall

**WARNING:** This resets everyone's XP of specified channel, either text or voice. If no channel is specified it resets both, everyone's Text and Voice XP.

```yaml
Aliases:
- reseteveryone

Usage:
;level resetall [channel=both]

Examples:
# To reset everyone's text XP.
;level resetall text

# To reset everyone's voice XP.
;level resetall voice

# To reset everyone's both text and voice XP.
;level resetall 
```


### ;level configure

Configure many Levels settings in your server and customize it as you want it to be.

**Available Configurations**

- `stack` -- Determines if the roles given as level rewards should be stacked or not. Meaning if its
set to `no`, the role rewards for earlier levels will be removed automatically on attaining the next level.

```yaml
Aliases:
- config
- configs
- configuration

Usage:
;level configure [channel=text] [stack=yes]

Examples:
# Disable roles stack for text levelling.
;level configure no

# Disable roles stack for voice levelling.
;level configure voice no

# Enable back stacking of voice levelling.
;level configure voice yes
```
