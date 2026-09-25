#!/usr/bin/env python3
#
# Copyright this project and it's contributors
# SPDX-License-Identifier: Apache-2.0
#
# encoding=utf8

import json
import logging
import os
import sys
from typing import List
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slackify_markdown import slackify_markdown

SLACK_SECTION_TEXT_LIMIT = 3000

# Module-level logger (no handlers attached on import)
logger = logging.getLogger(__name__)


def setup_logging(level: int = logging.INFO) -> None:
    """Configures logging handlers. Only call this from CLI execution."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )


def format_release_notes(release_notes: str) -> str:
    """Convert Markdown to Slack mrkdwn and enforce the section limit."""
    formatted_notes = slackify_markdown(release_notes).rstrip("\n")
    if len(formatted_notes) > SLACK_SECTION_TEXT_LIMIT:
        logger.warning(
            "Release notes exceeded limit of %d characters (%d chars). Truncating text.",
            SLACK_SECTION_TEXT_LIMIT,
            len(formatted_notes)
        )
    return formatted_notes[:SLACK_SECTION_TEXT_LIMIT]


def main() -> None:
    """main function"""
    logger.info("Initializing Slack release notifier script...")

    try:
        project = os.environ['INPUT_PROJECT_NAME']
        client = WebClient(token=os.environ['INPUT_SLACK_BOT_TOKEN'])
        logo = os.environ['INPUT_PROJECT_LOGO']
        release_version = os.environ['INPUT_RELEASE_VERSION']
        release_name = f"{project} {release_version}"
        release_url = os.environ['INPUT_RELEASE_URL']
        release_notes = os.environ['INPUT_RELEASE_NOTES']
        raw_channel = os.environ['INPUT_SLACK_CHANNEL']
    except KeyError as e:
        logger.error("Missing required environment variable: %s", e)
        sys.exit(1)

    channel = raw_channel if raw_channel.startswith("#") else f"#{raw_channel}"

    logger.info("Preparing release notification for '%s' to channel '%s'", release_name, channel)

    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{release_name}*"
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
        }
    ]

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

    try:
        logger.info("Sending message to Slack...")
        response = client.chat_postMessage(
            channel=channel,
            attachments=json.dumps(attachments),
            blocks=json.dumps(blocks),
            text=release_name,
            icon_url=logo
        )
        if response.get("ok"):
            logger.info("Successfully posted release message to %s (ts: %s)", channel, response.get("ts"))
        else:
            logger.warning("Slack API returned non-OK status: %s", response)

    except SlackApiError as e:
        logger.error("Slack API error posting message: %s", e.response["error"])
        logger.error("Response status code: %s", e.response.status_code)
        sys.exit(1)
    except Exception as e:
        logger.exception("Unexpected error encountered while sending notification: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    setup_logging()
    main()
