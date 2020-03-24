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

### role

Manage reaction based roles throughout different channels. Reactions are added to specified messages. Members can react to automatically get the desired roles.

```yaml
Aliases:
- roles

Usage:
;reaction role
```

#### add

Setup reaction roles over any custom message you wish or you may skip this parameter to let bot post a embed displaying list of provided roles.

To use custom message, you can pass its shareable URL which can be obtained by right clicking over your custom message and click \`Copy Message Link\` from the floating menu. If you're using this command in same channel your message is present, you can simply pass its message ID.

```yaml
Aliases:
- setup
- set

Usage:
'reaction role add [message] <roles...>
```

#### remove

Remove reaction roles from provided message.  
To use custom message, you can pass its shareable URL which can be obtained by right clicking over your custom message and click \`Copy Message Link\` from the floating menu. If you're using this command in same channel your message is present, you can simply pass its message ID.

```yaml
Aliases:
- delete

Usage:
;reaction role remove <message>
```

