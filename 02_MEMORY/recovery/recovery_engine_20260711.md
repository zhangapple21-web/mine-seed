# Recovery Engine Report — 2026-07-11 18:52

## Overall Status

**BOT_ONLY**

- Suggested Action: `Bot session available for push. User session needs re-login.`
- Need Login: **NO**

## Scan Summary

- Total findings: 330
- Session files: 41
- Config files: 32

## Session Validation

- Alive (user): 0
- Alive (bot):  1
- Dead/invalid: 9

### Validation Details

| Session | Status | User | Is Bot | Need Login |
|---------|--------|------|--------|------------|
| tg_bot_Bot1_Invalid | not_authorized | - | - | YES |
| tg_bot_Bot2_Sck01Bot | alive | @Sck01Bot | True | NO |
| tg_collections | not_authorized | - | - | YES |
| tg_test_All False except App Hash | not_authorized | - | - | YES |
| tg_test_Allow App Hash | not_authorized | - | - | YES |
| tg_test_App Hash + Current Number | not_authorized | - | - | YES |
| tg_test_App Sandbox | not_authorized | - | - | YES |
| tg_test_Default (no settings) | not_authorized | - | - | YES |
| tg_test_Firebase + App Hash | not_authorized | - | - | YES |
| tg_test_Unknown Number + App Hash | not_authorized | - | - | YES |

## Recovery Result

```
Alive User Session: - 0
Alive Bot Session:  +1
Need Login:         NO

Suggested Action:
Bot session available for push. User session needs re-login.
```