# Slack Release Notifier 

Provides rich notifications to a specific Slack channel for releases

### Usage
```yml
name: Publish Release Notice to Slack

on:
  release:
    types:
      - released

jobs:
  publish:
    runs-on: ubuntu-latest
    timeout-minutes: 5

    steps:
    - name: Notify Slack
      id: slack
      with:
        # Project Name
        project_name: "My Project"
        # Slack Bot Token; follow instructions to get one at https://api.slack.com/tutorials/tracks/getting-a-token with scopes 'channels:read' and 'chat:write'
        slack_bot_token: ${{ secrets.SLACK_BOT_TOKEN }}
        # Slack Channel to post to
        slack_channel: "#release-announcements"
        # Project Logo
        project_logo: "https://artwork.aswf.io/other/aswf/text/aqua/aswf-text-aqua.png"
      uses: jmertic/slack-release-notifier@main
```
