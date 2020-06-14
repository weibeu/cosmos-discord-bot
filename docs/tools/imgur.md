---
description: Another utility plugin which provides few commands to directly interact with imgur API.
---

# Imgur

## ;imgur

Uploads provided URL or attached image to imgur.com and returns the direct URL of the image.

You can also specify either an **emoji** or **mention** someone to upload their avatar to imgur. If no URL is specified, returns the imgur URL of the user's avatar.


```yaml
Aliases:
- imgurfy
- imgurify

Usage:
;imgur [url]

Examples:
# Send an image along with this command to upload it.
;imgur

# Upload an existing image to imgur using its URL.
;imgur https://cdn.discordapp.com/attachments/401070542947352616/721773984189907098/unknown.png
```
