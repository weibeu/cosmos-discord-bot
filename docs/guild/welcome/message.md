---
description: A plugin to send customized welcome messages for newly joined members.
---

# Message

Lets you set fully customized template to use for Welcome Messages using different variables. Use `{variable}` in your template to use the variables.

### Valid Variables:

* `{id}` -- Discord ID of the member.
* `{mention}` -- Mentions the member.
* `{name}` -- Discord name of the member excluding their Discord discriminator.
* `{username}` -- Discord name of the member including their Discord discriminator.
* `{discriminator}` -- Discriminator of the member.

## ;welcome message

Displays the template being used for Welcome Messages if it has been set already.

{% hint style="success" %}
If [User Verification](../../moderation/user-verification.md) is enabled, welcome message is sent only after the member is verified.
{% endhint %}

{% hint style="success" %}
If [Welcome Banner](banner.md) is enabled, the Welcome Messages are included along with the welcome banners.
{% endhint %}

```yaml
Aliases:
- msg

Usage:
;welcome message
```

### ;welcome message set

Setup and enable Welcome Messages using provided template. The Welcome Messages are sent to the current or any specified channel whenever a new user joins the server.

```yaml
Usage:
;welcome message set [channel] <message>
```

### ;welcome message remove

Remove and disable Welcome Messages from the server.

```yaml
Aliases:
- delete

Usage:
;welcome message remove
```

## ;welcome directmessage

Displays the template being using for Direct Welcome Messages if it has been set already.

{% hint style="success" %}
Direct welcome messages are sent just after user joins the server irrespective of [User Verification](../../moderation/user-verification.md).
{% endhint %}

```yaml
Aliases:
- dm
- directmsg

Usage:
;welcome directmessage
```

### ;welcome directmessage set

Setup and enable Direct Welcome Messages using provided template. The Welcome Messages are sent as direct message whenever a new user joins the server.

```yaml
Usage:
;welcome directmessage set <message>
```

### ;welcome directmessage remove

Remove and disable Direct Welcome Messages from the server.

```yaml
Aliases:
- delete

Usage:
;welcome directmessage remove
```

