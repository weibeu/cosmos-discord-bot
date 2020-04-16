---
description: >-
  Manage permissions of bot in different channels as well as of its various
  functions.
---

# Cosmos Permissions

## ;disable

Disables provided [function ](../reference.md#the-functions-hierarchy)from one or multiple channels which are specified.

A function can be any of the commands, plugins or galaxies which are allowed to be disabled.

```yaml
Usage:
;disable <function> [channels...]
```

### ;disable channels

Disables bot commands and most of its automatic messages in current or provided channels.

```yaml
Aliases:
- channel

Usage:
;disable channels [channels...]
```

## ;enable

Enables provided [function ](../reference.md#the-functions-hierarchy)in all of the specified channels.

A function can be any of the commands, plugins or galaxies.

```yaml
Usage:
;enable<function> [channels...]
```

### ;enable channels

Enables back bot commands and its automatic messages in current or provided channels if it was disabled previously.

```yaml
Aliases:
- channel

Usage:
;enable channels [channels...]
```

