# 🌟 GLAM RENT - Alquiler de Vestidos de Gala

Sistema completo de comercio electrónico con panel de administración y pasarela de pagos.

## ✨ Características

- 🛍️ **Tienda Online** - Catálogo de productos con carrito de compras
- 👑 **Panel de Administración** - Gestión completa de productos y pedidos
- 💳 **Pagos con Stripe** - Procesamiento seguro de pagos
- 📦 **Sistema de Pedidos** - Seguimiento completo de órdenes
- 🏷️ **Categorías** - Organización de productos
- 📸 **Subida de Imágenes** - Para productos nuevos
- 📊 **Dashboard** - Estadísticas en tiempo real

## 🚀 Inicio Rápido

### 1. Instalar Dependencias
```bash
pip3 install -r requirements.txt
```

### 2. Configurar Stripe
```bash
# Copia el archivo de ejemplo
cp .env.example .env

# Edita .env y añade tus claves de Stripe
# Obtén claves de prueba en: https://dashboard.stripe.com/test/apikeys
```

El archivo `.env` ya está creado localmente con claves de prueba funcionales.

### 3. Inicializar Base de Datos
```bash
python3 init_admin.py
python3 seed_products.py
```

### 4. Iniciar Servidor
```bash
./start_server.sh
# o
python3 app.py
```

## 🔑 Credenciales

### Administrador
- **URL:** http://localhost:5000/admin.html
- **Email:** admin@glamrent.com
- **Contraseña:** admin123

### Tarjeta de Prueba (Stripe)
- **Número:** 4242 4242 4242 4242
- **Fecha:** 12/25
- **CVV:** 123

## 📚 Documentación

- **[INSTRUCCIONES_ADMIN.md](INSTRUCCIONES_ADMIN.md)** - Guía completa de uso
- **[RESUMEN_IMPLEMENTACION.md](RESUMEN_IMPLEMENTACION.md)** - Detalles técnicos
- **[CHECKLIST_PRUEBAS.md](CHECKLIST_PRUEBAS.md)** - Lista de verificación

## 🛠️ Tecnologías

- **Backend:** Flask + SQLAlchemy
- **Base de Datos:** SQLite
- **Pagos:** Stripe API
- **Frontend:** HTML5, CSS3, JavaScript
- **Autenticación:** JWT

## 📱 URLs

- **Tienda:** http://localhost:5000
- **Panel Admin:** http://localhost:5000/admin.html

## 🔐 Seguridad

- Las claves de Stripe están en variables de entorno (`.env`)
- El archivo `.env` NO se sube a GitHub
- Contraseñas hasheadas con bcrypt
- Autenticación con JWT tokens

## 📝 Notas

- Las claves de Stripe están en el archivo `.env` local
- Para producción, usa tus propias claves de Stripe
- Cambia la contraseña del admin después del primer uso

---

**Desarrollado por:** 766ms  
**Licencia:** MIT
