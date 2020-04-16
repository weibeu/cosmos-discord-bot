---
description: Assign roles to new members right after they join your server.
---

# Roles

{% hint style="success" %}
If [User Verification](../../moderation/user-verification.md) is enabled, welcome roles are added only after the member is verified.
{% endhint %}

## ;welcome roles

Displays the list of roles being assigned to every new members joining the server.

```yaml
Aliases:
- role

Usage:
;welcome roles
```

### ;welcome roles set

Set roles which will be assigned to every new members joining your server.

```yaml
Aliases:
- setup
- add

Usage:
;welcome roles set <roles...>
```

### ;welcome roles remove

Remove all of the roles from welcome roles if set any.

```yaml
Aliases:
- delete
- clear

Usage:
;welcome roles remove
```

