@echo off
REM ============================================================
REM  Abre o notebook da analise no Jupyter, no navegador.
REM  Basta dar DUPLO-CLIQUE neste arquivo.
REM ============================================================
chcp 65001 >nul
set PYTHONUTF8=1
cd /d "%~dp0"

echo.
echo ===========================================================
echo   Abrindo o notebook da analise...
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

echo Instalando dependencias e o Jupyter (so demora na primeira vez)...
%PY% -m pip install --quiet --upgrade pip
%PY% -m pip install --quiet -r requirements.txt
%PY% -m pip install --quiet notebook
echo.

echo Iniciando o Jupyter. O navegador vai abrir sozinho.
echo Para encerrar, feche esta janela preta.
echo.
%PY% -m notebook analise_banco_mundial_FINAL.ipynb
