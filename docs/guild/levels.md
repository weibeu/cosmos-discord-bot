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

Displays any rewards set for specified or all of the levels.

Optionally pass `text` to view Text Levels rewards and `voice` for Voice Levels rewards.

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

