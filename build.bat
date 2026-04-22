@echo off
echo Сборка GoArt VPN...

pip install pyinstaller

:: Собираем папку (не один файл - надёжнее и быстрее)
pyinstaller --onedir ^
    --noconsole ^
    --name "GoArtVPN" ^
    goartvpn.py

:: Копируем bin\ и config.json в собранную папку
xcopy /E /I /Y bin dist\GoArtVPN\bin
copy /Y config.json dist\GoArtVPN\config.json

echo.
echo Готово! Папка: dist\GoArtVPN\
echo Запускать: dist\GoArtVPN\GoArtVPN.exe
echo.
echo Для раздачи на другие компы — копируй всю папку dist\GoArtVPN\
pause
