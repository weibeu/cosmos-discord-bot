---
description: A plugin to manage and setup Role Shop in server.
---

# Settings

### ;roleshop create

Create a new or use specified role for the Role Shop.

```yaml
Usage:
;roleshop create <points> <role>
```

### ;roleshop remove

Remove specified role from the Role Shop.

It displays an interactive reaction based menu to choose your desired role if it's not specified.

```yaml
Aliases:
- delete

Usage:
;roleshop remove [role]
```

### ;roleshop modify

Make changes to existing Role Shop role.

```yaml
Aliases:
- edit
```

#### ;roleshop modify points

Modify points required to redeem or purchase role.

It displays an interactive reaction based menu to choose your desired role if it's not specified.

```yaml
Aliases:
- point

Usage:
;roleshop modify points <new_points> [role]
```

## ;givepoints

Generate and give points to specified member. You can also specify negative points to remove points.

```yaml
Aliases:
- givepoint

Usage:
;givepoints <points> <member>
```

