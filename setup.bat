@echo off
echo ========================================
echo   CONFIGURACION AUTOMATICA - ECOFACT
echo ========================================
echo.

echo [1/6] Creando entorno virtual...
python -m venv venv
if %errorlevel% neq 0 (
    echo ERROR: No se pudo crear el entorno virtual
    echo Verifica que Python este instalado
    pause
    exit /b 1
)

echo [2/6] Activando entorno virtual...
call venv\Scripts\activate.bat

echo [3/6] Instalando dependencias...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: No se pudieron instalar las dependencias
    pause
    exit /b 1
)

echo [4/6] Configurando variables de entorno...
if not exist .env (
    copy .env.example .env
    echo Archivo .env creado con configuracion de Neon
) else (
    echo Archivo .env ya existe
)

echo [5/8] Ejecutando migraciones...
python manage.py migrate
if %errorlevel% neq 0 (
    echo ERROR: No se pudieron ejecutar las migraciones
    pause
    exit /b 1
)

echo [6/8] Creando usuarios predeterminados...
python manage.py create_test_users
if %errorlevel% neq 0 (
    echo ADVERTENCIA: No se pudieron crear usuarios de prueba
)

echo [7/8] Creando superusuario...
python manage.py create_superuser
if %errorlevel% neq 0 (
    echo ADVERTENCIA: No se pudo crear superusuario
)

echo [8/8] Recopilando archivos estaticos...
python manage.py collectstatic --noinput
if %errorlevel% neq 0 (
    echo ADVERTENCIA: No se pudieron recopilar archivos estaticos
)

echo [8/8] Configuracion completada!
echo.
echo ========================================
echo   CONFIGURACION EXITOSA
echo ========================================
echo.
echo Usuarios disponibles:
echo - Superadmin: superadmin@ecofact.com / superadmin123
echo - Admin: admin@ecofact.com / admin123
echo - Vendedor: vendedor@ecofact.com / vendedor123
echo - Cliente: cliente@ecofact.com / cliente123
echo.
echo URLs importantes:
echo - Aplicacion: http://localhost:8001/
echo - Login: http://localhost:8001/login/
echo - Admin: http://localhost:8001/admin/
echo.
echo Para iniciar el servidor ejecuta:
echo python manage.py runserver 8001
echo.
echo ¡Tu proyecto EcoFact esta listo para usar!
echo.
pause