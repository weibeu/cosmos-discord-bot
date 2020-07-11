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

## ;rafflepoints

Raffles points among the members who react to the confetti reaction to specified number of winners.
Defaults to 1 winner. By default, raffle will last till 7 seconds. If you want it to last for desired time then you should specify when it should end.

```yaml
Aliases:
- rafflepoint

Usage:
;rafflepoints <points> [winners=1] [end]

Examples:
# Raffle 100 points among 2 winner and lasts for 30 seconds.
;rafflepoints 100 2 30seconds

# Raffle 300 points among 1 winner and lasts for 7 seconds.
;rafflepoints 300
```

### ;roleshop resetall

WARNING: This command will reset everyone's roleshop points. This will not affect already owned roleshop roles.

```yaml
Aliases:
- reseteveryone

Usage:
;roleshop resetall
```

