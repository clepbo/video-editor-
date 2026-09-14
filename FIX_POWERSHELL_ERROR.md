# Fix Your Current PowerShell Errors

Your log shows 2 problems:

### Error 1: `C:\Python311\python.exe` not recognized
**Meaning:** Python 3.11 is NOT installed yet at that path. You need to install it first.

### Error 2: `.\venv\Scripts\Activate.ps1` not recognized
**Meaning:** You're in `C:\Users\Teasoo Consulting 3` not in `video-editor-` folder, so venv doesn't exist there. Also your old Python 3.14 venv is still active `(venv)` - need to deactivate.

### Exact Fix - Do This In Order

**Step 1: Install Python 3.11 FIRST**

1. Go to: https://www.python.org/downloads/release/python-3119/
2. Scroll down to **Files** -> Click **Windows installer (64-bit)**
3. Run installer:
   - ✅ Check **Add python.exe to PATH** (first screen, bottom)
   - Click **Customize installation**
   - Check all boxes -> Next
   - Check **Install for all users**
   - **Change install location to:** `C:\Python311` (type it manually)
   - Click **Install**
4. Wait for install to finish

**Step 2: Open NEW PowerShell as Admin**

- Press Win+X -> Windows PowerShell (Admin) or Terminal (Admin)
- Run:
```powershell
py --list
```
Should show:
```
 -V:3.14 * Python 3.14 (64-bit)
 -V:3.11   Python 3.11 (64-bit)
```
If you see 3.11, good. If not, restart PC and try again.

**Step 3: Fix Your Current PowerShell Session**

You are currently in `C:\Users\Teasoo Consulting 3` with old venv active. Run these EXACT commands:

```powershell
# 1. Deactivate old Python 3.14 venv
deactivate

# 2. Go to your project folder (USE QUOTES because of spaces)
cd "C:\Users\Teasoo Consulting 3\video-editor-"

# 3. Delete old venv (Python 3.14 one)
Remove-Item -Recurse -Force venv -ErrorAction SilentlyContinue
rmdir /s /q venv 2>$null; echo "Old venv deleted"

# 4. Create NEW venv with Python 3.11 using py launcher (more reliable than path)
py -3.11 -m venv venv

# 5. Allow scripts to run (PowerShell blocks them by default)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force

# 6. Activate new venv
.\venv\Scripts\Activate.ps1

# 7. Verify - MUST show 3.11, not 3.14
python --version
# Should be: Python 3.11.9

# 8. Upgrade pip and install
python -m pip install --upgrade pip
pip install -r starter-app/requirements_minimal.txt

# If that works, then full:
pip install -r starter-app/requirements_full.txt

# 9. Test
python -c "import customtkinter; print('OK')"

# 10. Run
python starter-app/viral_editor_pro.py
```

**If `py -3.11` says not found:**

Try these alternatives one by one:

```powershell
# Try full path after you installed to C:\Python311
C:\Python311\python.exe --version

# If that works, use it to create venv:
C:\Python311\python.exe -m venv venv

# Or try:
py -3.11-64 -m venv venv
python3.11 -m venv venv
```

**Alternative: Use CMD instead of PowerShell (Simpler, no execution policy issues)**

1. Press Win+R -> Type `cmd` -> Enter
2. Run:
```cmd
cd /d "C:\Users\Teasoo Consulting 3\video-editor-"
rmdir /s /q venv
py -3.11 -m venv venv
venv\Scripts\activate.bat
python --version
pip install -r starter-app/requirements_minimal.txt
python starter-app/viral_editor_pro.py
```

CMD uses `activate.bat` not `.ps1` and doesn't have execution policy problems.

**Step 4: Move Project to Avoid Spaces (Recommended after it works)**

Once it works, move to `C:\video-editor-\` to avoid future space issues:

```powershell
# In File Explorer, copy C:\Users\Teasoo Consulting 3\video-editor- to C:\video-editor-
# Then in PowerShell:
cd C:\video-editor-
.\venv\Scripts\Activate.ps1
```

### Quick One-Liner Fix Script

Save this as `fix.bat` in your project folder and double-click:

```bat
@echo off
cd /d "%~dp0"
echo Deleting old venv...
rmdir /s /q venv 2>nul
echo Creating venv with Python 3.11...
py -3.11 -m venv venv
call venv\Scripts\activate.bat
python --version
echo Installing minimal requirements...
pip install -r starter-app\requirements_minimal.txt
echo Done! Run: python starter-app\viral_editor_pro.py
pause
```

### Still Fails?

Paste output of these commands:

```powershell
py --list
where python
python --version
dir "C:\Python311\"
```
