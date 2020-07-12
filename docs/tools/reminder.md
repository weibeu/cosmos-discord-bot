---
description: Reminder which reminds you of something in distant future.
---

# Reminder

## ;reminder

Set reminder to get notified at specified time in future in the same channel in which you created the reminder.

You can specify when in number of formats. To include a message with reminder, just include it
after you specify the when parameter.

To set your reminder with a time difference, begin with 'in '. Otherwise normally specify the date
and time you want to set reminder to.

**Note:** Reminders smaller than 60 seconds will not be persisted. Meaning if the bot restarts or the universe
explodes and resets during this duration then, such reminders will not be triggered.

```yaml
Aliases:
- remind
- remindme
- timer
- alarm

Usage:
;remind [when]

Examples:
# Set reminder with a message to trigger in certain duration.
;remind in 4days 2hours Feed my hungry cat.

# Set reminder with a message to trigger on some specific date time.
;remind 7 September at 4PM Watch thaaat stream on YouTube.

# Set anonymous reminders.
;remind in 10minutes
```

### ;reminder remove

Removes the reminder with specified reminder ID. You can get the reminder ID from ;reminders command.

```yaml
Aliases:
- delete

Usage:
;reminder remove <reminder_id>

Examples:
;reminder remove 5f0b1a8bd48ea9c5a8bd893c
```

## ;reminders

Displays list of reminders which has been created by you.

```yaml
Usage:
;reminders
```
