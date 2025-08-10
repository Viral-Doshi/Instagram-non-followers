## Instagram Non‑Followers

Find who you follow that doesn’t follow you back. Fast, local, and simple.

### Install

```bash
pip3 install -r requirements.txt
```

### Configure (top of `nonfollowers.py`)

- Set either:
  - **USERNAME**, **PASSWORD**, **SESSIONID**, **CSRFTOKEN**, **DS_USER_ID** (recommended)
- Optional: **SESSION_FILE** (save session settings) and **HTTP_PROXY** if your IP is blocked.

### How to get cookies (Chrome & Safari)

- **Chrome**:
  1) Log into `instagram.com`
  2) Open DevTools → Application → Storage → Cookies → `https://www.instagram.com`
  3) Copy values of `sessionid`, `csrftoken`, `ds_user_id`

- **Safari**:
  1) Safari → Settings → Advanced → enable “Show Develop menu”
  2) Log into `instagram.com`
  3) Develop → Show Web Inspector → Storage/Resources → Cookies → `https://www.instagram.com`
  4) Copy `sessionid`, `csrftoken`, `ds_user_id`

Paste those into the variables at the top of `nonfollowers.py`.

### Run

```bash
python3 nonfollowers.py
```

It will print each username (one per line) and a short summary.

### Notes

- If login is blocked, switch networks (VPN/hotspot) or set `HTTP_PROXY`.
- Only your own data; nothing is uploaded anywhere.

