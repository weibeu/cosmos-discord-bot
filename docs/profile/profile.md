---
description: Plugin which implements Cosmos Profile.
---

# Profile

## ;profile

Displays your Cosmos Profile or of specified member.

```yaml
Usage:
;profile [user]
```

### ;profile description

Displays currently set profile description.

```yaml
Aliases:
- text

Usage:
;profile description
```

#### ;profile description set

Add description to your profile. The profile description can't exceed char length of 250.

```yaml
Aliases:
- modify
- edit
- change

Usage:
;profile description set <description>
```

### ;profile birthday

Displays your birthday if it has been set already.

```yaml
Aliases:
- birthdate
- bday

Usage:
;profile birthday
```

#### ;profile birthday set

Set your birthday to show up on the Cosmos Profile. [DD-MM-YYYY].

```yaml
Usage:
;profile birthday set <birthday>

Examples:
;profile birthday set 31-12-1997
;profile birthday set 31/12/1997
;profile birthday set 31 December 1997
```

## ;rep

Add a reputation point to specified member.

```yaml
Usage:
;rep [user]
```

