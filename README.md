# 🎬 Seerr to ntfy Notifier

A lightweight Python Flask webhook server that transforms **Seerr** (Jellyseerr / Overseerr) request notifications into clean, action-oriented push notifications delivered via **ntfy.sh**.

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0+-000000?style=flat-square&logo=flask&logoColor=white)
![ntfy](https://img.shields.io/badge/ntfy-Push%20Notifications-1A202C?style=flat-square&logo=ntfy&logoColor=white)

---

## ✨ Features

- **Automated Event Mapping**: Formats and triggers custom alerts for 6 core Seerr events:
  - ⏳ Pending requests
  - 🤖 Auto-approved requests
  - ✅ Manually approved requests
  - ❌ Declined requests
  - 🍿 Media available
  - ⚠️ Media addition failures (Radarr/Sonarr)
- **Rich Media Attachments**: Automatically resolves relative TMDb poster URLs to display media artwork directly in push notifications.
- **Custom Branding**: Displays custom app icons and contextual ntfy tags/emojis per notification state.
- **Noise Filtering**: Silently ignores non-request payloads (e.g. issue reporting) to keep notifications clean.
- **Environment Config**: Uses `.env` for easy configuration of topic secrets, endpoints, and server ports.

---

## 🛠️ Project Structure

```text
seerr-notifier/
├── .env                  # Environment variables (ignored by git)
├── .gitignore            # Git exclusion rules
├── app.py                # Main Flask webhook server
└── requirements.txt      # Python dependencies
