# Raspberry Pi CI/CD & Systemd Setup Guide

This guide explains how to set up your Raspberry Pi so that it automatically starts your bot on boot using `systemd`, and automatically updates your bot whenever you push code to GitHub using a Self-Hosted Runner.

---

## Step 1: Set up the Python Virtual Environment
We want to keep the bot's dependencies isolated in a virtual environment (`.venv`). Run this inside the `Rye-Chan-Bot` folder on your Pi:

```bash
cd <your-path>/Rye-Chan-Bot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Step 2: Set up the Systemd Service
This will tell your Raspberry Pi to automatically start the bot in the background when it boots up.
Configure it as per your system.

1. **Copy the service file** to the systemd directory:
   ```bash
   sudo cp setup/rye-chan.service /etc/systemd/system/
   ```
2. **Reload systemd** so it sees the new file:
   ```bash
   sudo systemctl daemon-reload
   ```
3. **Enable the service** so it starts on boot:
   ```bash
   sudo systemctl enable rye-chan
   ```
4. **Start the service** right now:
   ```bash
   sudo systemctl start rye-chan
   ```
*(You can check the bot's logs anytime by running: `sudo journalctl -u rye-chan -f`)*

---

## Step 3: Install the GitHub Actions Self-Hosted Runner
Because your Pi is on a home network behind a router, we install a background program (the "Runner") that reaches out to GitHub to look for new code.

1. Go to your GitHub Repository in your web browser.
2. Click **Settings** > **Actions** > **Runners**.
3. Click the green **New self-hosted runner** button.
4. Select **Linux** and **ARM64** (or **ARM** depending on your Pi OS).
5. GitHub will provide you with a list of `Download` and `Configure` commands. 
   - **Important:** Run these commands in a new directory on your Pi (e.g., `/home/<user>/actions-runner`), NOT inside your bot's folder!
6. When configuring, you can just press `Enter` to accept all the defaults.
7. Install the runner as a background service by running:
   ```bash
   sudo ./svc.sh install
   sudo ./svc.sh start
   ```

---

## Step 4: Give the Runner permission to restart the bot
When GitHub Actions pulls new code, it needs to restart your bot by running `sudo systemctl restart rye-chan`. By default, `sudo` asks for a password, which will freeze the automated pipeline. We need to allow the `pi` user to restart *only* this specific service without a password.

1. Open the sudoers configuration:
   ```bash
   sudo visudo
   ```
2. Scroll to the very bottom of the file and paste this exact line:
   ```text
   pi ALL=(ALL) NOPASSWD: /bin/systemctl restart rye-chan
   ```
3. Save and exit (Ctrl+X, then Y, then Enter).

---

## You're Done!
From now on, whenever you merge code into the `master` branch on GitHub:
1. GitHub Actions will contact your Pi.
2. The Pi will pull the latest code.
3. The Pi will install any new requirements.
4. The Pi will restart the `rye-chan` service.
