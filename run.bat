@echo off
setlocal
cd /d "%~dp0"
set "PY=%PYTHON_BIN%"
if "%PY%"=="" (
  where python3.14 >nul 2>nul && set "PY=python3.14" || (
    where python >nul 2>nul && set "PY=python" || (
      echo No python found (set PYTHON_BIN) 1>&2
      exit /b 1
    )
  )
)
echo Using: 
%PY% -c "import sys; print(sys.executable, sys.version.split()[0])"
%PY% -m py_compile run_lab.py test_lab.py || exit /b %ERRORLEVEL%
%PY% run_lab.py || exit /b %ERRORLEVEL%
%PY% -m unittest -v || exit /b %ERRORLEVEL%
