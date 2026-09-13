@echo off
setlocal
set "REPO=%~dp0"
set "PYTHON_EXE=C:\Users\Hp\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
set "PORT=8766"
set "SERVER_SCRIPT=%REPO%serve_adt_book.py"

for /f "tokens=2 delims=," %%P in ('tasklist /fi "imagename eq python.exe" /fo csv /nh') do (
  rem noop: tasklist warmup for permissions-free process check
)

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$port=%PORT%; $repo='%REPO%'; $python='%PYTHON_EXE%'; $script='%SERVER_SCRIPT%'; $exists=Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'python.exe' -and $_.CommandLine -like '*serve_adt_book.py*' -and $_.CommandLine -like ('*' + $port + '*') }; if (-not $exists) { Start-Process -FilePath $python -ArgumentList $script,'--host','127.0.0.1','--port',$port -WorkingDirectory $repo -WindowStyle Hidden; Start-Sleep -Seconds 2 }; Start-Process ('http://127.0.0.1:' + $port + '/index.html')"
endlocal
