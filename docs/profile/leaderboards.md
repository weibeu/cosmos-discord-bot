---
description: Leaderboard commands over various properties of user profile.
---

# Leaderboards

## ;leaderboards

Displays top members with maximum chat experience points or specified stats. You can also specify any from global stats to directly check the the global leaderboards.

```yaml
Stats:
- chat
- voice
- points
- streaks

Aliases:
- leaderboard
- lb

Usage:
;leaderboards [stats=chat]

Examples:
# Check points leaderboards.
;lb points

# Check global reputation points leaderboards.
;lb reps
```

### ;leaderboards global

Displays top users with maximum chat experience or specified stats earned globally across all servers.

```yaml
Stats:
- chat
- voice
- reps
- bosons
- fermions
- streaks

Aliases:
- globals
- cosmos

Usage:
;leaderboards global [stats=chat]

Examples:
# Check global chat leaderboards.
;lb global

# Check global voice leaderboards.
;lb global voice

# Check global bosons leaderboards.
;lb global bosons
```

