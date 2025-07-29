@echo off
setlocal

:: --- Configuration ---
set "PYTHON_VERSION=3.10"
set "PROJECT_NAME=greater_tables_project"
REM set "PROJECT_REPO=https://github.com/mynl/%PROJECT_NAME%.git"
set "PROJECT_REPO=c:\s\telos\python\greater_tables_project"
set "BUILD_DIR=C:\tmp\%PROJECT_NAME%_rtd_build"
set "VENV_DIR=%BUILD_DIR%\venv"
set "HTML_OUTPUT_DIR=%BUILD_DIR%\html"
set "PORT=9800"

:: --- Prepare Environment ---
echo Cleaning previous build directory...
pushd C:\tmp
rmdir /s /q "%BUILD_DIR%" >nul 2>&1
mkdir "%BUILD_DIR%"

:: --- Clone Repository ---
echo Cloning repository...
git clone --depth 1 "%PROJECT_REPO%" "%BUILD_DIR%"
rem git clone "%PROJECT_REPO%" "%BUILD_DIR%"
if %ERRORLEVEL% NEQ 0 (
    echo Git clone failed. Exiting.
    exit /b %ERRORLEVEL%
)

cd "%BUILD_DIR%"

:: --- Fetch latest changes ---
rem echo Fetching latest changes...
rem git fetch origin --force --prune --prune-tags --depth 50 refs/heads/master:refs/remotes/origin/master
rem if %ERRORLEVEL% NEQ 0 (
rem     echo Git fetch failed. Exiting.
rem     exit /b %ERRORLEVEL%
rem )

:: --- Checkout master branch ---
rem echo Checking out master branch...
rem git checkout --force origin/master
rem if %ERRORLEVEL% NEQ 0 (
rem     echo Git checkout failed. Exiting.
rem     exit /b %ERRORLEVEL%
rem )

:: --- Setup Virtual Environment ---
echo Creating virtual environment for Python %PYTHON_VERSION%...
:: Assuming 'uv' is installed and available in PATH.
:: If not, you might need to install it: uv pip install uv
uv venv "%VENV_DIR%" --python %PYTHON_VERSION%
if %ERRORLEVEL% NEQ 0 (
    echo Failed to create virtual environment. Ensure uv and Python %PYTHON_VERSION% are available. Exiting.
    exit /b %ERRORLEVEL%
)

call "%VENV_DIR%\Scripts\activate.bat"
if %ERRORLEVEL% NEQ 0 (
    echo Failed to activate virtual environment. Exiting.
    exit /b %ERRORLEVEL%
)

:: --- Install Dependencies ---
echo Upgrading setuptools...
uv pip install --upgrade setuptools
if %ERRORLEVEL% NEQ 0 (
    echo Failed to upgrade setuptools. Exiting.
    exit /b %ERRORLEVEL%
)

echo Installing Sphinx...
uv pip install --upgrade sphinx
if %ERRORLEVEL% NEQ 0 (
    echo Failed to install Sphinx. Exiting.
    exit /b %ERRORLEVEL%
)

echo Installing project dependencies from pyproject.toml...
uv pip install --upgrade --no-cache-dir .[dev]
if %ERRORLEVEL% NEQ 0 (
    echo Failed to install project dependencies. Exiting.
    exit /b %ERRORLEVEL%
)

:: --- Build HTML Documentation ---
echo Building HTML documentation...
python -m sphinx -T -b html -d _build\doctrees -D language=en docs "%HTML_OUTPUT_DIR%"
if %ERRORLEVEL% NEQ 0 (
    echo HTML build failed. Exiting.
    exit /b %ERRORLEVEL%
)

echo.
echo HTML documentation built successfully in "%HTML_OUTPUT_DIR%"

:: --- Launch Web Server and Open Docs ---
echo Launching a simple web server for the documentation...
start /b cmd /c "cd /d "%HTML_OUTPUT_DIR%" && python -m http.server %PORT%"
echo Opening documentation in your default browser...
start "" "http://localhost:%PORT%"

:: --- Optional: Build LaTeX/PDF (commented out) ---
:: echo Building LaTeX/PDF documentation...
:: python -m sphinx -T -b latex -d _build\doctrees -D language=en docs "%BUILD_DIR%\pdf"
:: if %ERRORLEVEL% NEQ 0 (
::     echo LaTeX build failed. Exiting.
::     exit /b %ERRORLEVEL%
:: )
::
:: echo Running latexmk to generate PDF...
:: cd "%BUILD_DIR%\pdf"
:: latexmk -r latexmkrc -pdf -f -dvi- -ps- -jobname=archivum-project -interaction=nonstopmode
:: if %ERRORLEVEL% NEQ 0 (
::     echo PDF generation failed. Exiting.
::     exit /b %ERRORLEVEL%
:: )
:: cd "%BUILD_DIR%"
::
:: echo PDF documentation built successfully in "%BUILD_DIR%\pdf"

endlocal
