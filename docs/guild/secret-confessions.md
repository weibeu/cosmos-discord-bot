---
description: >-
  A plugin to spice up your community with secret confessions. It lets the
  members to confess anonymously in certain channel.
---

# Secret Confessions

## ;confessions

Lets you confess anonymously in specified server. Your identity might be visible to the server moderators.

{% hint style="danger" %}
You can make only one confession every 7 minutes.
{% endhint %}

```yaml
Aliases:
- confession
- confess

Usage:
;confess <server_id> <confession>
```

### ;confessions set

Set secret confessions to current or specified channel. Use [`on_confession` Logger](../moderation/logger.md) event to moderate confessions and keep track of their real identity.

```yaml
Aliases:
- setup
- enable

Usage:
;confessions set [channel]
```

### ;confessions remove

Remove secret confessions from the server.

```yaml
Aliases:
- delete
- disable

Usage:
;confessions remove
```

