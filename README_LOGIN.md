# Sistema de Login EcoFact

## Descripción
Sistema de autenticación con tres roles de usuario: Administrador, Vendedor y Cliente.

## Roles de Usuario

### Administrador
- Acceso completo al sistema
- Panel: `/admin-dashboard/`
- Permisos: Todas las funcionalidades

### Vendedor  
- Acceso a funciones de ventas
- Panel: `/vendedor-dashboard/`
- Permisos: Gestión de productos y ventas

### Cliente
- Acceso a funciones de cliente
- Panel: `/cliente-dashboard/`
- Permisos: Visualización de productos y facturas

## Configuración

### 1. Crear usuarios de prueba
```bash
python manage.py create_test_users
```

### 2. Credenciales de prueba
- **Admin**: admin@ecofact.com / admin123
- **Vendedor**: vendedor@ecofact.com / vendedor123  
- **Cliente**: cliente@ecofact.com / cliente123

## Uso

1. Acceder a `/login/`
2. Introducir email y contraseña
3. El sistema redirige automáticamente según el rol:
   - Admin → `/admin-dashboard/`
   - Vendedor → `/vendedor-dashboard/`
   - Cliente → `/cliente-dashboard/`

## Seguridad

- Autenticación basada en email
- Protección por roles con decoradores
- Redirección automática según permisos
- CSRF protection habilitado

## URLs Principales

- `/login/` - Página de login
- `/logout/` - Cerrar sesión
- `/admin-dashboard/` - Panel administrador
- `/vendedor-dashboard/` - Panel vendedor  
- `/cliente-dashboard/` - Panel cliente