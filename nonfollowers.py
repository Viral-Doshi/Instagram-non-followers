#!/usr/bin/env python3

"""
Hey guys !!! Have fun playing around with this script.
Find Instagram accounts you follow who don't follow you back by logging in
with your username, password, and some cookie details. Edit the USERNAME, PASSWORD, SESSIONID, CSRFTOKEN, DS_USER_ID variables
below, then run:

    python3 nonfollowers.py

Requires: instagrapi (pip install -r requirements.txt)
"""

from __future__ import annotations

import sys
import json
from pathlib import Path
from typing import Dict, Set, Optional, Iterable, Any

try:
    from instagrapi import Client
    from instagrapi.exceptions import LoginRequired, ChallengeRequired, TwoFactorRequired, ClientError
except Exception as exc:  # pragma: no cover - import guidance
    sys.stderr.write(
        "Missing dependency: instagrapi. Install it with: pip install -r requirements.txt\n"
    )
    raise


# =====================
# CONFIGURE THESE VALUES
# =====================
# - Either provide USERNAME and PASSWORD (may be blocked by challenges),
#   or provide the browser cookies (SESSIONID + CSRFTOKEN + DS_USER_ID) for a
#   more reliable login from this machine.
#
# How to get cookies from browsers:
# Chrome:
#   1) Open instagram.com and ensure you are logged in
#   2) Open DevTools (View > Developer > Developer Tools)
#   3) Application tab > Storage > Cookies > https://www.instagram.com
#   4) Copy values for: sessionid, csrftoken, ds_user_id
# Safari:
#   1) Safari > Settings > Advanced > check "Show Develop menu in menu bar"
#   2) Open instagram.com and ensure you are logged in
#   3) Develop > Show Web Inspector
#   4) Storage (or Resources) tab > Cookies > https://www.instagram.com
#   5) Copy values for: sessionid, csrftoken, ds_user_id
# Notes:
#   - Paste cookie values exactly as shown (sessionid may contain % characters)
#   - If login is still blocked, try switching networks or set HTTP_PROXY below

USERNAME: str = "_viral_doshi"
PASSWORD: str = "Hotspot@19"

# Optional: Set a path to persist session settings (reduces challenges between runs).
# Example:
#   SESSION_FILE = "/absolute/path/instagram_settings.json"
SESSION_FILE: Optional[str] = None

# Browser cookies (recommended)
SESSIONID: Optional[str] = "5044814313%3AQwRxOdmGIulNjB%3A0%3AAYdxrCeQzqJjejmJxdUOVuPXBjxngMW7yve4wGdjtA"
CSRFTOKEN: Optional[str] = "rWHadAvza51mDx7BRFXv9i"
DS_USER_ID: Optional[str] = "5044814313"

# Optional: HTTP proxy to route requests (can help with IP blocks). Example:
#   HTTP_PROXY = "http://user:pass@host:port"
HTTP_PROXY: Optional[str] = None


def normalize_username(username: str) -> str:
    return username.strip().lstrip("@").lower()


def collect_usernames(container: Any) -> Set[str]:
    """Collect usernames from a dict[int, UserShort] or list[UserShort]."""
    usernames: Set[str] = set()
    if isinstance(container, dict):
        iterable: Iterable[Any] = container.values()
    elif isinstance(container, list):
        iterable = container
    else:
        iterable = []
    for user in iterable:
        try:
            usernames.add(normalize_username(getattr(user, "username")))
        except Exception:
            continue
    return usernames

def main() -> int:
    if not SESSIONID and (not USERNAME or USERNAME == "your_username_here" or not PASSWORD or PASSWORD == "your_password_here"):
        sys.stderr.write(
            "Please set USERNAME and PASSWORD (or set SESSIONID) at the top of the file.\n"
        )
        return 1

    client = Client()

    # Load optional session settings to reduce login challenges
    if SESSION_FILE:
        path = Path(SESSION_FILE).expanduser()
        if path.is_file():
            try:
                settings_text = path.read_text(encoding="utf-8")
                client.load_settings(json.loads(settings_text))
            except Exception:
                pass

    # Optional proxy
    if HTTP_PROXY:
        try:
            client.set_proxy(HTTP_PROXY)
        except Exception:
            pass

    try:
        if SESSIONID:
            # Pre-inject cookies for both public and private sessions
            try:
                client.public.cookies.set("sessionid", SESSIONID, domain=".instagram.com", path="/")  # type: ignore[attr-defined]
            except Exception:
                pass
            try:
                client.private.cookies.set("sessionid", SESSIONID, domain=".instagram.com", path="/")  # type: ignore[attr-defined]
            except Exception:
                pass
            if CSRFTOKEN:
                try:
                    client.public.cookies.set("csrftoken", CSRFTOKEN, domain=".instagram.com", path="/")  # type: ignore[attr-defined]
                except Exception:
                    pass
                try:
                    client.private.cookies.set("csrftoken", CSRFTOKEN, domain=".instagram.com", path="/")  # type: ignore[attr-defined]
                except Exception:
                    pass
            if DS_USER_ID:
                try:
                    client.public.cookies.set("ds_user_id", DS_USER_ID, domain=".instagram.com", path="/")  # type: ignore[attr-defined]
                    client.private.cookies.set("ds_user_id", DS_USER_ID, domain=".instagram.com", path="/")  # type: ignore[attr-defined]
                except Exception:
                    pass

            # Validate and attach session via library method
            client.login_by_sessionid(SESSIONID)
        else:
            client.login(USERNAME, PASSWORD)
    except TwoFactorRequired:
        sys.stderr.write(
            "Login failed: Two-factor authentication required. This script does not handle interactive 2FA.\n"
        )
        return 2
    except ChallengeRequired:
        sys.stderr.write(
            "Login failed: Instagram requested additional verification (challenge).\n"
        )
        return 2
    except LoginRequired:
        sys.stderr.write("Login failed: Login required or invalid credentials.\n")
        return 2
    except ClientError as exc:
        sys.stderr.write(f"Login failed: {exc}\n")
        return 2

    # Dump session after successful login, if requested
    if SESSION_FILE:
        try:
            settings_dict = client.get_settings()
            Path(SESSION_FILE).expanduser().write_text(json.dumps(settings_dict), encoding="utf-8")
        except Exception:
            pass

    # Resolve own user id
    try:
        my_user_id = client.user_id_from_username(USERNAME)
    except Exception as exc:
        sys.stderr.write(f"Failed to resolve user id for {USERNAME}: {exc}\n")
        return 3

    # Prefer private API over public GraphQL to avoid JSON issues
    try:
        # Some versions expose toggles for GraphQL usage
        try:
            client.use_graphql_only = False  # type: ignore[attr-defined]
        except Exception:
            try:
                client.use_graphql = False  # type: ignore[attr-defined]
            except Exception:
                pass

        # Fetch following and followers. These return dict[user_id, UserShort]
        try:
            try:
                following_container = client.user_following_v1(my_user_id)  # type: ignore[attr-defined]
            except Exception:
                following_container = client.user_following(my_user_id)

            try:
                followers_container = client.user_followers_v1(my_user_id)  # type: ignore[attr-defined]
            except Exception:
                followers_container = client.user_followers(my_user_id)
        except ClientError as exc:
            sys.stderr.write(f"Failed to fetch followers/following: {exc}\n")
            return 4
    except Exception as exc:
        sys.stderr.write(f"Unexpected error while toggling API/fetching: {exc}\n")
        return 4

    following_usernames: Set[str] = collect_usernames(following_container)
    followers_usernames: Set[str] = collect_usernames(followers_container)

    not_following_back = sorted(following_usernames - followers_usernames)

    for username in not_following_back:
        print(username)

    # Also print a small summary line to stderr
    sys.stderr.write(f"Total not following back: {len(not_following_back)}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

