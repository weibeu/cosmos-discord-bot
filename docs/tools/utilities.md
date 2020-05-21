---
description: >-
  This plugin provides few useful utility commands.
---

# Utilities

## ;embed

Make bot send a neat embed with all provided attributes. Useful for making server information sections.

You do NOT need to specify every property, only the ones you want.

**All properties and the syntax:**

- title=<words>
- description=<words>
- color=<hex_value>
- image=<url_to_image> (must be https)
- thumbnail=<url_to_image>
- author=<words> **OR** author=name=<words> icon=<url_to_image>
- footer=<words> **OR** footer=name=<words> icon=<url_to_image>
- field=name=<words> value=<words> (you can add as many fields as you want)
- ptext=<words>
                
**Note:**

- After the command is sent, the bot will delete your message and replace it with the embed.
- Make sure you have it saved or else you'll have to type it all again if the embed isn't how you want it.
- Hyperlink text like so: [text](https://www.whateverlink.com)
- Force a field to go to the next line with the added parameter inline=False

```yaml
Usage:
;embed [msg]

Examples:
;embed title=test this | description=some words | color=3AB35E | field=name=test value=test
```