# 🚀 DEPLOY TO ITCH.IO - STEP BY STEP

## ✅ Your Game Files Are Ready
- **Build folder:** `C:\Users\LENOVO\OneDrive\Documents\AvoidTheBlock\build\web`
- **Zip file:** `AvoidTheBlock-web.zip` (585 KB)

---

## 📋 UPLOAD INSTRUCTIONS (5 Minutes)

### STEP 1: Create Itch.io Account
1. Go to: https://itch.io
2. Click "Register" (top right)
3. Choose username (e.g., `sanjeevgames`)
4. Verify email

### STEP 2: Create a New Game Page
1. After login, click your **avatar** → **"Dashboard"**
2. Click **"Create new project"** (or "New Game")
3. Fill in:
   - **Title:** `Avoid The Block`
   - **Project URL:** `avoid-the-block` (auto-filled based on title)
   - **Description:** 
     ```
     A fast-paced survival game where you dodge falling obstacles. 
     Use arrow keys or A/D to move, Shift/Q/E to dash. 
     Unlock themes and power-ups as you progress!
     ```
   - **Classification:** Select `Game`
   - **Uploads:** Leave empty for now
4. Click **"Save"**

### STEP 3: Upload Your Game Build
On your game page, scroll to **"Uploads"** section:

1. Click **"Upload file"**
2. **Browse** and select the **`build/web` folder** (or the zip file)
   - You can drag-and-drop the entire folder here
3. **IMPORTANT SETTINGS:**
   - ☑️ Check: **"This file will be played in the browser"**
   - Select **Display as:** `HTML` (or `Pygame` if available)
   - Leave "Default" as the display option
4. Click **"Upload"**

### STEP 4: Configure as Playable
After upload completes:
1. Itch.io will ask: "How should this file be displayed?"
   - Select: **"HTML"** 
   - Click **"Set as default"** if prompted
2. The platform should auto-detect `index.html`

### STEP 5: Make it Public
At the bottom of your game page:
1. Under **"Visibility & Access"**:
   - Set to: **"Public"**
2. Click **"Save"**

### STEP 6: Share Your Game! 🎉
Your game is now live at:
```
https://[your-username].itch.io/avoid-the-block
```

Example: `https://sanjeevgames.itch.io/avoid-the-block`

---

## 🎯 WHAT HAPPENS AFTER UPLOAD

✅ **First visit:** 30-60 seconds loading (Python runtime compiles)
✅ **Repeat visits:** 2-3 seconds (cached by Itch.io CDN)
✅ **Works on:** Desktop, tablet, mobile
✅ **Players can:** Rate, comment, rate your game

---

## 📊 Optional: Add Custom Domain
Later, you can:
- Buy a domain (e.g., `avoidtheblock.com`)
- Link it to Itch.io in Settings → Domain

---

## 🎮 GAME FEATURES ON ITCH.IO

Your deployed game includes:
- ✅ Themes (unlock by reaching score thresholds)
- ✅ Power-ups (shield, slow, multiplier, dash)
- ✅ Leaderboard (stored locally per browser)
- ✅ Developed by Sanjeev (in-game credit)
- ✅ Responsive controls (keyboard)

---

## 📝 NOTE

- No backend needed — fully static HTML5 build
- Itch.io handles CDN + hosting for free
- Your game is shareable immediately after upload

Go to https://itch.io and create your account now! 🚀
