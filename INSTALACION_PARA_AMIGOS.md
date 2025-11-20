# 🚀 Guía de Instalación Rápida para Nuevos Colaboradores

## ⚡ Instalación en 2 Minutos

### Para Windows:
```bash
git clone https://github.com/Infona2049/front-ecofact.git
cd front-ecofact
setup.bat
```

### Para Linux/Mac:
```bash
git clone https://github.com/Infona2049/front-ecofact.git
cd front-ecofact
chmod +x setup.sh
./setup.sh
```

Ya está listo!

Después de ejecutar el script, simplemente:

```bash
python manage.py runserver 8001
```

Ve a: **http://localhost:8001/login/**

 Usuarios para Probar

| Rol | Email | Contraseña |
|-----|-------|------------|
| **Cliente** | cliente@ecofact.com | cliente123 |
| **Vendedor** | vendedor@ecofact.com | vendedor123 |
| **Admin** | admin@ecofact.com | admin123 |
| **Superadmin** | superadmin@ecofact.com | superadmin123 |

URLs Importantes

- **Login:** http://localhost:8001/login/
- **Registro:** http://localhost:8001/registro/
- **Admin:** http://localhost:8001/admin/

 Lo que el script hace automáticamente:

1. ✅ Crea entorno virtual
2. ✅ Instala dependencias
3. ✅ Configura base de datos en la nube
4. ✅ Ejecuta migraciones
5. ✅ Crea todos los usuarios
6. ✅ Configura archivos estáticos

¿Problemas?

### Error: "Python no encontrado"
Instala Python desde: https://python.org

### Error: "Git no encontrado"  
Instala Git desde: https://git-scm.com

### Los logos no cargan
```bash
python manage.py collectstatic --noinput
```

Datos Importantes
 
- **Base de datos:** Compartida en la nube (Neon)
- **Puerto:** 8001 (no 8000)
- **Registro:** Solo permite crear clientes
- **Admin:** Para crear vendedores/admins usar el panel de Django

Colaboración

1. Haz tu propia rama: `git checkout -b mi-feature`
2. Haz tus cambios
3. Commit: `git commit -m "descripción"`
4. Push: `git push origin mi-feature`
5. Crea Pull Request

---
**¡Bienvenido al equipo EcoFact!** 