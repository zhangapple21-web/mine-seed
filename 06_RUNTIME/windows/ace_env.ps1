# ACE Runtime Environment Variables
# This file is sourced by start_runtime scripts
# DO NOT commit real secrets to GitHub - use miner_env.sh.tpl for templates

# TG Bot Token (Bot 2 @Sck01Bot - Bot 1 is invalid)
$env:TG_BOT_TOKEN_2 = "8446702999:AAHw51HYX_EwZhnzmJpQFUy734SnaZpzsCI"

# TG Chat ID (fill in after sending a message to @Sck01Bot)
# To get your chat_id: send any message to @Sck01Bot, then run:
#   python 06_RUNTIME\connectors\tg_pusher.py --token $env:TG_BOT_TOKEN_2 --test
#   or visit: https://api.telegram.org/bot8446702999:AAHw51HYX_EwZhnzmJpQFUy734SnaZpzsCI/getUpdates
$env:TG_CHAT_ID = "5016609451"

# ntfy.sh topic for fallback notifications
$env:NTPY_TOPIC = "ace-cloud-worker"

# GitHub token (for git push) - load from miner_env.sh or set manually
# DO NOT hardcode tokens here - GitHub Push Protection will block it
# $env:GITHUB_TOKEN = "<set your token in environment or miner_env.sh>"