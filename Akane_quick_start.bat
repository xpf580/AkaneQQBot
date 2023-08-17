@echo off

start powershell -NoExit -Command "cd .\unidbg-fetch-qsign-1.1.6; .\#start.bat"

REM 打开第一个终端并进入虚拟环境，然后执行 bot.py
start powershell -NoExit -Command "cd .\AkaneBot; ..\AkaneENV\Scripts\Activate.ps1; python .\bot.py"

REM 等待一段时间确保第一个终端已启动，然后打开第二个终端并进入虚拟环境，然后执行 go-cqhttp

start powershell -NoExit -Command "cd .\go-cqhttp-windows-i386; ..\AkaneENV\Scripts\Activate.ps1; .\go-cqhttp.exe -faststart"

REM 等待一段时间确保第二个终端已启动，然后打开第三个终端并进入虚拟环境，然后执行 manage.py

start powershell -NoExit -Command "cd .\chat; ..\AkaneENV\Scripts\Activate.ps1; python .\manage.py runserver"



