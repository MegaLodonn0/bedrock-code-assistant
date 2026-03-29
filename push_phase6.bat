@echo off
REM AWS Native Modernization Phase 6 - Push Commands (Windows)

echo.
echo ===============================================
echo Phase 6: AWS Native Modernization
echo ===============================================
echo.

echo 📊 CHANGES SUMMARY:
echo -------------------
git diff origin/main..main --stat
echo.

echo 📝 COMMITS TO PUSH:
echo -------------------
git log --oneline origin/main..main
echo.

echo 📦 FILES TO BE ADDED:
echo -------------------
git diff origin/main..main --name-status
echo.

echo ===============================================
echo READY TO PUSH
echo ===============================================
echo.
echo Execute this command:
echo.
echo   git push origin main
echo.
echo Or with verbose output:
echo.
echo   git push origin main -v
echo.

pause
