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

### description

Displays currently set profile description.

```yaml
Aliases:
- text

Usage:
;profile description
```

#### set

Add description to your profile. The profile description can't exceed char length of 250.

```yaml
Aliases:
- modify
- edit
- change

Usage:
;profile description set <description>
```

### birthday

Displays your birthday if it has been set already.

```yaml
Aliases:
- birthdate
- bday

Usage:
;profile birthday
```

#### set

Set your birthday to show up on the Cosmos Profile.

```yaml
Usage:
;profile birthday set <birthday>
```

## ;rep

Add a reputation point to specified member.

```yaml
Usage:
;rep [user]
```

