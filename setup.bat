@echo off

rem ### const value Start ###
set WARNING=WARNING: 
set ERROR=ERROR: 
rem ### const value  End  ###

rem venv 作成パス
set VENVPATH="%~dp0.venv"
rem venv スクリプトパス
set SCRIPTSPATH="%VENVPATH%\Scripts"

rem This file is UTF-8 encoded, so we need to update the current code page while executing it
for /f "tokens=2 delims=:." %%a in ('"%SystemRoot%\System32\chcp.com"') do (
    set _OLD_CODEPAGE=%%a
)
if defined _OLD_CODEPAGE (
    "%SystemRoot%\System32\chcp.com" 65001 > nul
)

echo ### Start Setup. ###

echo|set /p="python install ... "
where /Q python || ( echo. && decho %ERROR%python has not been installed! && pause && exit /b )
echo ok

rem venv が作成されていれば venv は作成しない
echo|set /p="create venv ... "
if not exist %VENVPATH% (
    rem venv をこのスクリプトと同階層に作成
    call python -m venv %VENVPATH%
    echo ok
) else (
    echo ok
    echo %WARNING%Already exist venv! Please remove %VENVPATH% if you want to clean setup.
)

rem venv をアクティブ化
call %SCRIPTSPATH%\activate

echo|set /p="install library ... "
rem ライブラリインストール
call pip --disable-pip-version-check --quiet install -r %~dp0requirements.txt
echo ok

echo.
rem インストール後の環境
call pip --disable-pip-version-check list

rem venv を非アクティブ化
call %SCRIPTSPATH%\deactivate

echo.
echo ### Finished Setup. ###

pause