---
description: Create interactive giveaways in your server.
---

# Giveaway
Create interactive giveaways in your server.

There are two ways you can host a giveaway in your server. You may either make use of the [`;giveaway`](#giveaway) command or include some special syntax in your own message to make bot trigger for the giveaway over this message.

## Custom Message Trigger

**SYNTAX:** `... keyword **reward** giveaway ...`

You can make use of this syntax in anywhere in your message. Cosmos will recognize it automatically and trigger the giveaway with reason enclosed inside `**...**`. Check out the following flexible examples.

- `... Katya is hosting **Free One Months Nitro!** giveaway ...`
- `... We really thank Arkham to host **Steam game Key** giveaway ...`
- `... So make sure to participate in **Fall Guys Steam Key** giveaway ...`
- `... The Cosmos is sponsoring **3 Months free Nitro** giveaway ...` 


## ;giveaway

Creates giveaway in the server and waits for members to participate by reacting to the message.

You must always specify the duration of the giveaway to let members to participate. It can be in format of xseconds, xmins, xhours, xweeks ...

By default it randomly chooses one winner from all members who had participated. To change, specify desired number of winners to pick randomly.

```yaml
Aliases:
- ga
- giveaways

Usage:
;giveaway <duration> [winners=1] [channel] <reward>

Examples:
;giveaway 2days 3 #giveaways 3 Months Discord Nitro
;giveaway 20hours Fall Guys Steam Key!
```
