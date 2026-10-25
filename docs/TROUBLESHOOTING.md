# Troubleshooting (Windows setup)

Common problems when setting up ETHIO-CYBERGUARD on Windows, and how to fix them.

## 1. `git` is not recognized

**Symptom:** PowerShell says `The term 'git' is not recognized as the name of a cmdlet...`

**Cause:** Git is not installed, or PowerShell was opened before the install finished.

**Fix:**
1. Install Git from the official site (https://git-scm.com/download/win), or run:
   `winget install --id Git.Git -e --source winget`
2. **Close PowerShell completely and open a new window.** Old windows do not see new installs.
3. Check: `git --version`

## 2. The browser warns that the installer "isn't commonly downloaded"

**Cause:** Edge shows this for new or rarely downloaded files, including fresh Git releases.

**Fix:** Download only from the official site, click the download's **...** menu, then **Keep**. To be safe, compare the file's SHA-256 hash with the one on the official release page:
`Get-FileHash .\Git-installer.exe -Algorithm SHA256`
If the browser keeps blocking it, use `winget` instead (see problem 1).

## 3. `python` or `node` is not recognized

**Fix:**
- Install Python 3.10+ from python.org and tick **"Add python.exe to PATH"** on the first installer screen. If `python` still fails, try `py --version`.
- Install the Node.js LTS (version 20 or higher) from nodejs.org.
- Open a **new** PowerShell window and check: `python --version`, `node --version`, `npm --version`.

## 4. Virtual environment will not activate

**Symptom:** `.\venv\Scripts\Activate.ps1 cannot be loaded because running scripts is disabled on this system`

**Fix (current user only):**
`Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`
Then run `.\venv\Scripts\Activate.ps1` again. The prompt should start with `(venv)`.

## 5. Copying the environment file

On Windows PowerShell use:
`copy .env.example .env`

The values in `.env.example` that start with `CHANGE_ME` are placeholders. Replace each one with your own value before running outside demo mode. Generate secrets with:
`python -c "import secrets; print(secrets.token_urlsafe(32))"`
If you change `POSTGRES_PASSWORD`, use the same password inside `DATABASE_URL`.

## 6. Port already in use

**Symptom:** the API (port 8000) or the web app (port 5173) fails to start because the port is busy.

**Fix:** find the program using the port: `netstat -ano | findstr :8000`
Close that program, or start the server on a different port.

## 7. Live demo page shows 404

The demo is published from the `gh-pages` branch. A repository admin must set
**Settings > Pages > Source = Deploy from a branch, Branch = `gh-pages`, folder = `/ (root)`**.
Contributors without admin access cannot see this setting.

## Still stuck?

Open an issue on GitHub and include the exact error message, your Windows version, and the output of `git --version`, `python --version` and `node --version`.
