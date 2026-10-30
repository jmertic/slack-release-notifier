#!/usr/bin/env python3
#
# Copyright this project and its contributors
# SPDX-License-Identifier: Apache-2.0
#
# encoding=utf8

import argparse
import json
import logging
import sys
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
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def format_release_notes(release_notes: str) -> str:
    """Convert Markdown to Slack mrkdwn and enforce the section limit."""
    formatted_notes = slackify_markdown(release_notes).rstrip("\n")
    if len(formatted_notes) > SLACK_SECTION_TEXT_LIMIT:
        logger.warning(
            "Release notes exceeded limit of %d characters (%d chars). Truncating text.",
            SLACK_SECTION_TEXT_LIMIT,
            len(formatted_notes),
        )
    return formatted_notes[:SLACK_SECTION_TEXT_LIMIT]


def parse_args() -> argparse.Namespace:
    """Parses command line arguments."""
    parser = argparse.ArgumentParser(
        description="Notify a Slack channel of new GitHub releases."
    )
    parser.add_argument(
        "--slack-bot-token",
        required=True,
        help="Slack Bot User OAuth Token (xoxb-...)",
    )
    parser.add_argument(
        "--slack-channel",
        required=True,
        help="Slack channel ID or name to post to",
    )
    parser.add_argument(
        "--project-name",
        required=True,
        help="Name of the project",
    )
    parser.add_argument(
        "--project-logo",
        required=True,
        help="Public URL for project logo image",
    )
    parser.add_argument(
        "--release-version",
        required=True,
        help="Release version string (e.g., v1.0.0)",
    )
    parser.add_argument(
        "--release-url",
        required=True,
        help="URL to the GitHub release page",
    )
    parser.add_argument(
        "--release-notes",
        required=True,
        help="Markdown formatted release notes",
    )
    return parser.parse_args()


def main() -> None:
    """main function"""
    logger.info("Initializing Slack release notifier script...")

    args = parse_args()

    project = args.project_name
    client = WebClient(token=args.slack_bot_token)
    logo = args.project_logo
    release_version = args.release_version
    release_name = f"{project} {release_version}"
    release_url = args.release_url
    release_notes = args.release_notes

    # Keep channel IDs (e.g. C0123456789) intact; prefix named channels with #
    raw_channel = args.slack_channel
    if raw_channel.startswith("#") or raw_channel.startswith("C"):
        channel = raw_channel
    else:
        channel = f"#{raw_channel}"

    logger.info(
        "Preparing release notification for '%s' to channel '%s'",
        release_name,
        channel,
    )

    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{release_name}*",
            },
            "accessory": {
                "type": "image",
                "image_url": logo,
                "alt_text": project,
            },
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "View Github Release",
                        "emoji": True,
                    },
                    "value": "view_github_release",
                    "url": release_url,
                }
            ],
        },
    ]

    attachments = [
        {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": format_release_notes(release_notes),
                    },
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
            icon_url=logo,
        )
        if response.get("ok"):
            logger.info(
                "Successfully posted release message to %s (ts: %s)",
                channel,
                response.get("ts"),
            )
        else:
            logger.warning("Slack API returned non-OK status: %s", response)

    except SlackApiError as e:
        logger.error("Slack API error posting message: %s", e.response["error"])
        logger.error("Response status code: %s", e.response.status_code)
        sys.exit(1)
    except Exception as e:
        logger.exception(
            "Unexpected error encountered while sending notification: %s", e
        )
        sys.exit(1)


if __name__ == "__main__":
    setup_logging()
    main()
