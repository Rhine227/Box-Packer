@echo off
echo Initializing Git repository for Box Packer...
echo.

REM Initialize git repository
git init

REM Add all files
git add .

REM Create initial commit
git commit -m "Initial commit: Box Packer v1.0.0 - Optimal pallet arrangement calculator"

echo.
echo Git repository initialized successfully!
echo.
echo Next steps:
echo 1. Create a new repository on GitHub (https://github.com/new)
echo 2. Name it "box-packer" or your preferred name
echo 3. Run these commands to push to GitHub:
echo.
echo    git branch -M main
echo    git remote add origin https://github.com/YOURUSERNAME/box-packer.git
echo    git push -u origin main
echo.
echo Replace YOURUSERNAME with your actual GitHub username
echo.
pause
