@echo off
:: Запускать от имени администратора!
:: Копирует нужные DLL из ALTVPN в папку bin\

set SRC=C:\Program Files\ALTVPN
set DST=%~dp0bin

echo Копирую файлы из %SRC% в %DST%...

copy "%SRC%\openconnect.exe"         "%DST%\"
copy "%SRC%\wintun.dll"              "%DST%\"
copy "%SRC%\libopenconnect-5.dll"    "%DST%\"
copy "%SRC%\libssl-1_1-x64.dll"      "%DST%\"
copy "%SRC%\libcrypto-1_1-x64.dll"   "%DST%\"
copy "%SRC%\libxml2-2.dll"           "%DST%\"
copy "%SRC%\liblzo2-2.dll"           "%DST%\"
copy "%SRC%\libgcc_s_dw2-1.dll"      "%DST%\"
copy "%SRC%\libwinpthread-1.dll"      "%DST%\"
copy "%SRC%\iconv.dll"               "%DST%\"
copy "%SRC%\zlib1.dll"               "%DST%\"
copy "%SRC%\libssp-0.dll"            "%DST%\"
copy "%SRC%\libssl-1_1.dll"          "%DST%\"
copy "%SRC%\libcrypto-1_1.dll"       "%DST%\"

echo.
echo Готово! Теперь запусти: python goartvpn.py
pause
