# 🖼️ AI Background Remover - Telegram Web App

A powerful and lightweight **Telegram Web App** (TWA) that allows users to remove image backgrounds instantly. This app is designed to be integrated seamlessly with bots on the **Bots.Business** platform.

---

## 🚀 Features
* ✨ **Instant Removal:** High-quality background removal using AI.
* 📱 **Native Experience:** Opens directly inside Telegram with a smooth interface.
* 📤 **Easy Upload:** Support for drag-and-drop or file selection.
* 📥 **One-Tap Download:** Save your processed PNG images directly to your device.
* ⚡ **Integrated with Bots.Business:** Built-in logic to communicate with your Telegram bot.

---

## 🛠️ Setup Guide

### 1. Host on GitHub Pages
1. Upload your `index.html` (and other assets) to this repository.
2. Go to **Settings** > **Pages**.
3. Under **Branch**, select `main` and click **Save**.
4. Copy your live URL (e.g., `https://yourusername.github.io/your-repo/`).

### 2. Configure in Bots.Business
Create a command (e.g., `/start` or `/bg`) in your **Bots.Business** dashboard and paste the following **BJS** code:

```javascript
var webAppUrl = "YOUR_GITHUB_PAGES_LINK_HERE";
Extra Environment: PYTHON_VERSION = 3.9

Api.sendMessage({
  text: "Click the button below to remove the background from your images:",
  reply_markup: {
    inline_keyboard: [
      [ { text: "✂️ Open BG Remover", web_app: { url: webAppUrl } } ]
    ]
  }
});
