@echo off
setlocal

set "VENV_DIR=.venv"

REM Verifica se o Python esta instalado
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Python nao encontrado. Por favor instale o Python.
    pause
    exit /b 1
)

REM Verifica se o ambiente virtual existe
if not exist "%VENV_DIR%" (
    echo Criando ambiente virtual...
    python -m venv "%VENV_DIR%"
)

REM Ativa o ambiente virtual
call "%VENV_DIR%\Scripts\activate"

REM Instala/Atualiza dependencias
echo Verificando dependencias...
pip install -r requirements.txt

REM Executa a aplicacao
echo Iniciando o Planejador CETI...
streamlit run app.py

pause
