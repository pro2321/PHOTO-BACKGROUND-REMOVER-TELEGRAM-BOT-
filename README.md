# 🖼️ AI Image Background Remover - Telegram Bot

A powerful and lightweight **Telegram Bot** that allows users to remove image backgrounds instantly. This bot is designed to be integrated seamlessly with host on the **Render** platform.

---

## 🚀 Features
* ✨ **Instant Removal:** High-quality background removal using **remove.bg** API key.
* 📤 **Easy to use:** Just upload an image and get your image.
* 📂 **Multiple formats:** Convert images directly into your chat(Jpeg/png/pdf/zip).
* 

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
