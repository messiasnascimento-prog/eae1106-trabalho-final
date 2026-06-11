@echo off
REM ============================================================
REM  Gera todos os graficos da analise (Educacao x Desemprego)
REM  Basta dar DUPLO-CLIQUE neste arquivo.
REM ============================================================
chcp 65001 >nul
set PYTHONUTF8=1
cd /d "%~dp0"

echo.
echo ===========================================================
echo   Investimento em Educacao e Desemprego - America Latina
echo ===========================================================
echo.

REM Localiza o Python (tenta "python", depois o launcher "py")
where python >nul 2>nul
if %errorlevel%==0 (
    set "PY=python"
) else (
    where py >nul 2>nul
    if %errorlevel%==0 (
        set "PY=py"
    ) else (
        echo [ERRO] Python nao foi encontrado no computador.
        echo Instale o Python 3 em https://www.python.org/downloads/
        echo e marque a opcao "Add Python to PATH" durante a instalacao.
        echo.
        pause
        exit /b 1
    )
)

echo Instalando as dependencias (so demora na primeira vez)...
%PY% -m pip install --quiet --upgrade pip
%PY% -m pip install --quiet -r requirements.txt
echo.

echo Gerando os 5 graficos...
%PY% gerar_graficos.py
echo.

echo ===========================================================
echo  Pronto! Os arquivos fig1...fig5 .png estao nesta pasta.
echo ===========================================================
echo.
pause
