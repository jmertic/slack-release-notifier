#!/usr/bin/env python3
#
# Copyright this project and it's contributors
# SPDX-License-Identifier: Apache-2.0
#
# encoding=utf8

import os
import json
from slackify_markdown import slackify_markdown
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import sys
from typing import List

SLACK_SECTION_TEXT_LIMIT = 3000

def format_release_notes(release_notes: str) -> str:
    """Convert Markdown to Slack mrkdwn and enforce the section limit."""

    formatted_notes = slackify_markdown(release_notes).rstrip("\n")
    return formatted_notes[:SLACK_SECTION_TEXT_LIMIT]


def main(args: List[str]) -> None:
    """main function

    Args:
        args: STDIN arguments
    """

    # now you can access the inputs like:
    #    f"Hello {os.environ["INPUT_NAME"]}"

    # you can write to output like:
    #   io.write_to_output({var: val, ...})

    project = os.environ['INPUT_PROJECT_NAME']
    client = WebClient(token=os.environ['INPUT_SLACK_BOT_TOKEN'])
    logo = os.environ['INPUT_PROJECT_LOGO']
    release_version = os.environ['INPUT_RELEASE_VERSION']
    release_name = "{} {}".format(project, release_version)
    release_url = os.environ['INPUT_RELEASE_URL']
    release_notes = os.environ['INPUT_RELEASE_NOTES']
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*{}*".format(release_name)
            },
            "accessory": {
                "type": "image",
                "image_url": logo,
                "alt_text": project
            }
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "View Github Release",
                        "emoji": True
                    },
                    "value": "view_github_release",
                    "url": release_url
                }
            ]
        }]
    attachments = [
        {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": format_release_notes(release_notes)
                    }
                }
            ]
        }
    ]

    channel = os.environ['INPUT_SLACK_CHANNEL']
    if not channel.startswith("#"):
        channel = f"#{channel}"

    try:
        response = client.chat_postMessage(
            channel=os.environ['INPUT_SLACK_CHANNEL'],
            attachments=json.dumps(attachments),
            blocks=json.dumps(blocks),
            text=release_name,
            icon_url=logo
        )
        assert response["message"]["text"] == release_name
    except SlackApiError as e:
        assert e.response["ok"] is False
        assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
        print(f"Got an error: {e.response['error']}")
        # Also receive a corresponding status_code
        assert isinstance(e.response.status_code, int)
        print(f"Received a response status_code: {e.response.status_code}")
