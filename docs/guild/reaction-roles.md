---
description: Plugin to implement reaction based roles in server.
---

# Reaction Roles

## ;reaction

It contains multiple reaction based sub-commands.

```yaml
Aliases:
- reactions

Usage:
;reaction
```

### ;reaction role

Manage reaction based roles throughout different channels. Reactions are added to specified messages. Members can react to automatically get the desired roles.

```yaml
Aliases:
- roles

Usage:
;reaction role
```

#### ;reaction role add

Setup reaction roles over any custom message you wish or you may skip this parameter to let bot post a embed displaying list of provided roles.

The **`stack`** parameter determines if these roles can be stacked over member or not. Defaults to True or Yes, meaning members can have more than one of these roles. Pass 'no' to restrict and let them have only one of these roles.

The **`permanent`** parameter determines if these roles once added, can be auto removed by members or not. Defaults to False or No. Meaning, members can remove this role anytime by clicking on the corresponding reaction if they already have this role. Specify no if you want to refrain them from automatically removing it.

To use custom message, you can pass its shareable URL which can be obtained by right clicking over your custom message and click \`Copy Message Link\` from the floating menu. If you're using this command in same channel your message is present, you can simply pass its message ID.

Moreover, if you want to use custom emotes, use a custom message and react with reactions you want to use over it. Cosmos will automatically consider them, but make sure you use the emotes which is from the server where Cosmos bot is present. 

```yaml
Aliases:
- setup
- set

Usage:
;reaction role add [message] [stack=yes] [permanent=no] <roles...>

Examples:
# For stacked roles. [Members can have more than one or all of these roles.]
;reaction role add 706571261114843146 @role1 @role2 @role3

# For unstacked roles. [Members can have only one of these roles.]
;reaction role add 706571261114843146 no @role1 @role2 @role3

# Use the default embed message.
;reaction role add "Select your regional role" no @Asia @UK @NA

# To set permanent stacked roles. [Members will not be able to remove it by themselves.]
;reaction role add 706571261114843146 yes yes @role1 @role2 @role3
# To set permanent unstacked roles.
;reaction role add 706571261114843146 no yes @role1 @role2 @role3
```

#### ;reaction role remove

Remove reaction roles from provided message.

To use custom message, you can pass its shareable URL which can be obtained by right clicking over your custom message and click \`Copy Message Link\` from the floating menu. If you're using this command in same channel your message is present, you can simply pass its message ID.

```yaml
Aliases:
- delete

Usage:
;reaction role remove <message>
```

