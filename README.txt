GoArt VPN — системный трей для Windows
=======================================

Структура папки:
    goartvpn/
    ├── goartvpn.py       <- главный файл
    ├── config.json       <- настройки (заполни password!)
    ├── README.txt
    └── bin/
        ├── openconnect.exe
        ├── wintun.dll
        ├── libopenconnect-5.dll
        ├── libssl-1_1-x64.dll
        ├── libcrypto-1_1-x64.dll
        ├── libxml2-2.dll
        ├── liblzo2-2.dll
        ├── libgcc_s_dw2-1.dll
        ├── libwinpthread-1.dll
        ├── iconv.dll
        ├── zlib1.dll
        └── ... (все остальные .dll из ALTVPN)

Установка на Windows:
1. Скопируй папку goartvpn/ на Windows
2. Открой config.json, впиши пароль в поле "password"
3. Скопируй ВСЕ .dll файлы из C:\Program Files\ALTVPN\ в папку bin\
4. Установи зависимости:
       pip install PyQt6 dnslib
5. Запусти:
       python goartvpn.py
   (UAC-диалог появится автоматически — нажми Да)

Использование:
- Иконка в трее: красная = отключено, жёлтая = подключение, зелёная = подключено
- Правый клик по иконке → Подключить / Отключить / Выход
