$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

$python = Join-Path $projectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        & py -3 -m venv .venv
    } elseif (Get-Command python -ErrorAction SilentlyContinue) {
        & python -m venv .venv
    } else {
        throw "Python topilmadi. Python 3 ni o'rnating va VS Code'ni qayta oching."
    }
    if ($LASTEXITCODE -ne 0) {
        throw "Virtual muhit yaratilmadi."
    }
}

$requirementsHash = (Get-FileHash requirements.txt -Algorithm SHA256).Hash
$hashFile = Join-Path $projectRoot ".venv\requirements.sha256"
$installedHash = if (Test-Path $hashFile) { (Get-Content $hashFile -Raw).Trim() } else { "" }
if ($requirementsHash -ne $installedHash) {
    & $python -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        throw "Kutubxonalarni o'rnatib bo'lmadi."
    }
    Set-Content -Path $hashFile -Value $requirementsHash
}

& $python manage.py migrate --noinput
if ($LASTEXITCODE -ne 0) {
    throw "Ma'lumotlar bazasini tayyorlab bo'lmadi."
}

$superuserStatus = & $python manage.py shell -c "from django.contrib.auth import get_user_model; print('1' if get_user_model().objects.filter(is_superuser=True).exists() else '0')"
if ($LASTEXITCODE -ne 0) {
    throw "Administrator hisobini tekshirib bo'lmadi."
}
if (($superuserStatus | Select-Object -Last 1).Trim() -ne "1") {
    Write-Host "Lokal administrator hisobini yarating."
    & $python manage.py createsuperuser
    if ($LASTEXITCODE -ne 0) {
        throw "Lokal admin hisobini yaratib bo'lmadi."
    }
}

& $python manage.py runserver 127.0.0.1:8000
