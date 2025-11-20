#!/bin/bash

echo "========================================"
echo "   CONFIGURACION AUTOMATICA - ECOFACT"
echo "========================================"
echo ""

echo "[1/6] Creando entorno virtual..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "ERROR: No se pudo crear el entorno virtual"
    echo "Verifica que Python3 este instalado"
    exit 1
fi

echo "[2/6] Activando entorno virtual..."
source venv/bin/activate

echo "[3/6] Instalando dependencias..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: No se pudieron instalar las dependencias"
    exit 1
fi

echo "[4/6] Configurando variables de entorno..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Archivo .env creado con configuracion de Neon"
else
    echo "Archivo .env ya existe"
fi

echo "[5/8] Ejecutando migraciones..."
python manage.py migrate
if [ $? -ne 0 ]; then
    echo "ERROR: No se pudieron ejecutar las migraciones"
    exit 1
fi

echo "[6/8] Creando usuarios predeterminados..."
python manage.py create_test_users
if [ $? -ne 0 ]; then
    echo "ADVERTENCIA: No se pudieron crear usuarios de prueba"
fi

echo "[7/8] Creando superusuario..."
python manage.py create_superuser
if [ $? -ne 0 ]; then
    echo "ADVERTENCIA: No se pudo crear superusuario"
fi

echo "[8/8] Recopilando archivos estaticos..."
python manage.py collectstatic --noinput
if [ $? -ne 0 ]; then
    echo "ADVERTENCIA: No se pudieron recopilar archivos estaticos"
fi

echo "[8/8] Configuracion completada!"
echo ""
echo "========================================"
echo "   CONFIGURACION EXITOSA"
echo "========================================"
echo ""
echo "Usuarios disponibles:"
echo "- Superadmin: superadmin@ecofact.com / superadmin123"
echo "- Admin: admin@ecofact.com / admin123"
echo "- Vendedor: vendedor@ecofact.com / vendedor123"
echo "- Cliente: cliente@ecofact.com / cliente123"
echo ""
echo "URLs importantes:"
echo "- Aplicacion: http://localhost:8001/"
echo "- Login: http://localhost:8001/login/"
echo "- Admin: http://localhost:8001/admin/"
echo ""
echo "Para iniciar el servidor ejecuta:"
echo "python manage.py runserver 8001"
echo ""
echo "¡Tu proyecto EcoFact esta listo para usar!"
echo ""