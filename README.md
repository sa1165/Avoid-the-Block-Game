Avoid The Block — Build & Deploy

This repo is a single-file Pygame game (`main.py`). The project uses `pygame` (see `requirements.txt`).

Developed by Sanjeev

Local quick start

- Ensure you have Python 3.10+ and pip installed.
- Install dependencies and run the game:

```powershell
python -m pip install -r requirements.txt
python .\main.py
```

Create a Windows distributable (recommended)

1) Use the provided PowerShell script to build on Windows (recommended):

```powershell
# from repo root
.\build_exe.ps1
```

This creates a folder build in `dist\AvoidTheBlock` containing `AvoidTheBlock.exe` and required files. The script uses `pyinstaller --onedir` and includes `leaderboard.json` as data.

Notes & options

- To produce a single-file binary change `--onedir` to `--onefile` in `build_exe.ps1` or run PyInstaller manually:

```powershell
pyinstaller --noconfirm --clean --onefile --add-data "leaderboard.json;." --name "AvoidTheBlock" main.py
```

- Building on Windows: PyInstaller builds should be run on the target platform for best results. The included GitHub Actions workflow (`.github/workflows/build-windows.yml`) will build on `windows-latest` when you push a tag `v*` or trigger manually via the Actions UI.

Web deployment (Browser / Itch.io)

Play online instantly — no installation needed!

1. Build the web version:

```powershell
python -m pip install pygbag
pygbag main.py
```

This creates a `build/web` folder with `index.html` and game files.

2. Deploy to Itch.io (FREE, fast CDN):

- Go to https://itch.io
- Create an account
- Create a new project titled "Avoid The Block"
- Upload the `build/web` folder
- Check "This file will be played in the browser"
- Set display type to "HTML"
- Make it public

Your game will be live at: `https://[your-username].itch.io/avoid-the-block`

First load: ~30-60 seconds (Python runtime loads)
Repeat loads: ~2-3 seconds (cached)

**For detailed step-by-step guide, see: [ITCH_IO_DEPLOY_GUIDE.md](./ITCH_IO_DEPLOY_GUIDE.md)**

CI (GitHub Actions)

- The workflow builds and uploads the `dist/AvoidTheBlock` directory as an artifact called `AvoidTheBlock-windows`.

Troubleshooting

- If the game window does not appear or rendering is blank, run locally from PowerShell to see console output:

```powershell
python .\main.py
```

- If PyInstaller misses data files, ensure `--add-data "leaderboard.json;."` is present. On non-Windows runners the `--add-data` separator is `:` instead of `;`.

Want a different target?

I can also:
- Prepare a ZIP release (source + venv instructions)
- Add itch.io publishing steps (butler)
- Produce a GitHub Action that auto-creates a GitHub Release and attaches the artifact

Tell me which one you'd like next.

Hosted game link (after release)

- After you push a tag (for example `v1.0`) the GitHub Actions workflow will run and create a Release. The public Release page will be at:

	`https://github.com/<your-username>/<your-repo>/releases/tag/v1.0`

	Replace `<your-username>` and `<your-repo>` with your GitHub details. The Release page will contain a downloadable artifact (for example `AvoidTheBlock-windows.zip`).

Itch.io alternative

- If you prefer a game page (play store style), create an itch.io project and upload the built folder or zip using `butler`:

```powershell
# after building with PyInstaller and zipping
# install butler: https://itch.io/docs/butler/installing/
# then login once and push
butler push AvoidTheBlock-windows.zip <your-itch-username>/avoid-the-block:windows
```

Credits

- Game window and README updated to show: `Developed by Sanjeev`.

If you'd like, I can also add an automated itch.io publish step, or produce a GitHub Pages landing page that links to the release. Tell me which hosting option you want me to set up next.

Placeholder audio

- If you don't provide audio assets, the game will auto-generate small placeholder WAV files on first run into `assets/sfx/` and `assets/music/`. This lets you hear immediate feedback (clicks, dings, and a short loop) without adding binary files to the repo.

Power-ups

- The game now includes collectible power-ups that fall like obstacles. Types:
	- `shield` — protects you from one collision
	- `slow` — slows falling blocks for ~2.2 seconds
	- `mult` — 2x score for ~10 seconds
	- `dash` — grants a dash charge for a quick lateral burst

- Controls: press `Shift` to dash in your current movement direction, or `Q` / `E` to dash left / right. Some themes are unlocked by high scores and power-ups occasionally spawn.

## 🎮 Play the Game
Click below to play the live version:

👉 https://precious-gnome-d44c79.netlify.app/

