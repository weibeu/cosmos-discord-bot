---
description: >-
  A plugin to implement text or voice levelling feature in server and related
  commands.
---

# Levels

## ;level

Displays current level and experience points.

```yaml
Aliases:
- levels

Usage:
;level [member]
```

### reward

Displays any rewards set for specified or all of the levels.  
Optionally pass `text` to view Text Levels rewards and `voice` for Voice Levels rewards.

```yaml
Aliases:
- rewards

Usage:
;level reward [channel=text] [level]
```

#### set

Set rewards for specified Text or Voice Levels.  
You can set one or multiple roles and optionally Guild Points as rewards.

```yaml
Usage:
;level reward set <level> [channel=text] [points=0] <roles...>
```

#### remove

Remove any Text or Voice Level rewards set for specified level.

```yaml
Aliases:
- delete

Usage:
;level reward [remove] <level> [channel=text]
```

