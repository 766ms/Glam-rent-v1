# 🌟 GLAM RENT - Venta de Vestidos de Gala

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
# 🌟 GLAM RENT - Sistema de Alquiler de Vestidos

Sistema web completo para alquiler de vestidos con panel de administración, carrito de compras y pasarela de pagos Stripe.

---

## 🚀 Instalación

### 1️⃣ Clonar el repositorio
```bash
git clone https://github.com/766ms/Glam-rent-v1.git
```

### 2️⃣ Instalar dependencias
opción 1
```bash
pip install -r requirements.txt
```
opción 2
```bash
pip install Flask flask-cors flask-sqlalchemy PyJWT Werkzeug stripe python-dotenv

```
opción 3 (cmd)
```bash
python3 -m pip install Flask flask-cors flask-sqlalchemy PyJWT Werkzeug stripe python-dotenv

```

### 3️⃣ Crear admin y categorías
Entrar en la subcarpeta
```bash
cd Glam-rent-v1 
```
Verificamos que estamos en el directorio correcto
```bash
dir
```
Colocar el siguiente comando para crear el admin
```bash
python -c "from app import app, db, Usuario, Categoria; from werkzeug.security import generate_password_hash; app.app_context().push(); db.create_all(); admin = Usuario(nombre='Admin', email='admin@glamrent.com', password=generate_password_hash('admin123'), es_admin=True); db.session.add(admin); db.session.commit(); print('✅ Admin creado'); [db.session.add(Categoria(nombre=c)) for c in ['Vestidos de Fiesta', 'Vestidos de Noche', 'Vestidos Casuales', 'Vestidos de Graduación', 'Vestidos de Coctel']]; db.session.commit(); print('✅ Categorías creadas')"
```

### 4️⃣ Agregar productos de ejemplo
```bash
python seed_products.py
```

### 5️⃣ Iniciar el servidor
```bash
python app.py
```

### 6️⃣ Abrir en el navegador
```
http://localhost:5000
```

---

## 👤 Credenciales de Admin

- **Email:** `admin@glamrent.com`
- **Password:** `admin123`

---

## 🔧 Si necesitas reiniciar la base de datos

### Windows:
```bash
del instance\tienda_vestidos.db
```

### Linux/Mac:
```bash
rm instance/tienda_vestidos.db
```

Luego vuelve a ejecutar desde el paso 3️⃣.

---

## 📦 Tecnologías

- **Backend:** Flask (Python)
- **Base de datos:** SQLite
- **Pagos:** Stripe
- **Frontend:** HTML5, CSS3, JavaScript

---

## ✨ Características

✅ Sistema de registro y autenticación  
✅ Carrito de compras persistente  
✅ Pasarela de pagos con Stripe (tarjetas de prueba)  
✅ Panel de administración completo  
✅ Gestión de productos con imágenes  
✅ Gestión de categorías  
✅ Gestión de pedidos y estados  
✅ Control de inventario/stock  

---

## 🎨 Panel de Admin

Una vez logueado como admin, verás el botón **"Panel Admin 👑"** en el header.

Desde el panel puedes:
- Ver estadísticas de ventas
- Gestionar pedidos (ver, cambiar estado, despachar)
- Agregar/editar/eliminar productos
- Subir imágenes de productos
- Crear categorías
- Controlar stock

---

## 💳 Tarjetas de Prueba Stripe

Para probar pagos usa:
- **Número:** `4242 4242 4242 4242`
- **Fecha:** Cualquier fecha futura
- **CVC:** Cualquier 3 dígitos
- **ZIP:** Cualquier código postal

---

## 📞 Soporte

Para problemas o preguntas, abre un issue en GitHub.

---

**Desarrollado por:** [Sara]  
**Año:** 2025

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
