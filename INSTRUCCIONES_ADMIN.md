# 🎉 GLAM RENT - Sistema de Administrador y Pasarela de Pagos

## 📋 Nuevas Funcionalidades Implementadas

### 1. Sistema de Administrador 👑
- Panel de administración completo
- Gestión de pedidos (ver, despachar, completar)
- Gestión de productos (añadir, editar, eliminar)
- Sistema de categorías
- Subida de imágenes para productos
- Estadísticas en tiempo real

### 2. Pasarela de Pagos con Stripe 💳
- Integración completa de Stripe
- Proceso de pago seguro
- Tarjetas de prueba funcionales
- Confirmación de pagos
- Reducción automática de stock

### 3. Sistema de Pedidos 📦
- Creación de pedidos desde el carrito
- Estados: pendiente, pagado, despachado, completado, cancelado
- Historial de pedidos para usuarios
- Gestión completa para administradores

## 🚀 Instalación

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
# o
pip3 install -r requirements.txt
```

### 2. Configurar claves de Stripe

**Opción A: Usar el archivo .env (RECOMENDADO)**
```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar .env y añadir tus claves de prueba de Stripe
# Las claves están en el archivo .env local que creaste durante la instalación
# O puedes obtener tus propias claves en: https://dashboard.stripe.com/test/apikeys
```

**Opción B: Variables de entorno del sistema**
```bash
export STRIPE_PUBLIC_KEY=pk_test_tu_clave_aqui
export STRIPE_SECRET_KEY=sk_test_tu_clave_aqui
```

### 3. Inicializar la base de datos

**Opción A: Inicialización completa (recomendada)**
```bash
# 1. Crear usuario administrador y categorías
python init_admin.py

# 2. Crear productos de ejemplo
python seed_products.py
```

**Opción B: Solo actualizar la base de datos**
Si ya tienes productos, solo ejecuta:
```bash
python init_admin.py
```

## 🔑 Credenciales de Acceso

### Administrador
- **Email:** admin@glamrent.com
- **Contraseña:** admin123
- **Panel Admin:** http://localhost:5000/admin.html

⚠️ **IMPORTANTE:** Cambia la contraseña después del primer login

### Tarjeta de Prueba (Stripe)
- **Número:** 4242 4242 4242 4242
- **Fecha:** Cualquier fecha futura (ej: 12/25)
- **CVV:** Cualquier 3 dígitos (ej: 123)
- **Código Postal:** Cualquier código

## 📱 Cómo Usar el Sistema

### Para Clientes:

1. **Navegar la tienda**
   - Ve a http://localhost:5000 o abre index.html
   - Explora los productos disponibles

2. **Agregar al carrito**
   - Haz clic en el precio del producto
   - Los productos se agregan al carrito

3. **Procesar pago**
   - Haz clic en el carrito
   - Click en "Proceder al Pago"
   - Inicia sesión si no lo has hecho
   - Ingresa dirección de envío
   - Ingresa datos de tarjeta de prueba
   - Confirma el pago

### Para Administradores:

1. **Acceder al panel**
   - Inicia sesión con las credenciales de admin
   - Verás un botón "Panel Admin 👑" en el header
   - O ve directamente a http://localhost:5000/admin.html

2. **Ver Estadísticas**
   - Panel principal muestra estadísticas en tiempo real
   - Total de pedidos, ventas, productos

3. **Gestionar Pedidos**
   - Sección "Pedidos"
   - Filtrar por estado
   - Ver detalles completos
   - Cambiar estado (Despachar, Completar, Cancelar)

4. **Gestionar Productos**
   - Sección "Productos"
   - Añadir nuevos productos con imagen
   - Editar stock y precios
   - Eliminar productos
   - Asignar categorías

5. **Gestionar Categorías**
   - Sección "Categorías"
   - Crear nuevas categorías
   - Ver productos por categoría

## 🔧 Configuración de Stripe

### Claves Actuales (Modo Prueba)
Las claves de Stripe ya están configuradas en el código:
- **Clave Pública:** pk_test_51QQvUMJYWQv45cg1...
- **Clave Secreta:** sk_test_51QQvUMJYWQv45cg1...

### Cambiar a tus propias claves

1. Crea una cuenta en [Stripe](https://stripe.com)

2. Obtén tus claves de API en modo prueba

3. Actualiza en `app.py`:
```python
stripe.api_key = 'tu_clave_secreta_de_stripe'
```

4. Actualiza en `admin.js` (función `initStripe`):
```javascript
stripe = Stripe('tu_clave_publica_de_stripe');
```

## 📊 Estructura de la Base de Datos

### Nuevas Tablas:
- **Usuario:** Ahora incluye campo `es_admin`
- **Categoria:** Almacena categorías de productos
- **Pedido:** Información de pedidos con estado
- **ItemPedido:** Productos individuales de cada pedido

### Relaciones:
- Producto → Categoria (muchos a uno)
- Pedido → Usuario (muchos a uno)
- ItemPedido → Pedido (muchos a uno)
- ItemPedido → Producto (muchos a uno)

## 🔄 Flujo de Compra

1. **Usuario agrega productos al carrito**
   → Se almacena en localStorage

2. **Usuario hace checkout**
   → Se crea un Pedido en estado "pendiente"
   → Se crean ItemPedido con los productos

3. **Usuario ingresa datos de pago**
   → Stripe crea un PaymentIntent
   → Cliente confirma el pago

4. **Pago exitoso**
   → Pedido cambia a estado "pagado"
   → Stock de productos se reduce
   → Carrito se vacía

5. **Admin gestiona el pedido**
   → Ve el pedido en el panel
   → Cambia estado a "despachado"
   → Finalmente a "completado"

## 🛠️ Endpoints de API Nuevos

### Categorías
- `GET /api/categorias` - Listar categorías
- `POST /api/categorias` - Crear categoría (Admin)

### Pedidos
- `POST /api/pedidos` - Crear pedido
- `GET /api/pedidos` - Mis pedidos
- `GET /api/admin/pedidos` - Todos los pedidos (Admin)
- `PUT /api/admin/pedidos/:id/estado` - Actualizar estado (Admin)

### Stripe
- `GET /api/stripe/config` - Obtener clave pública
- `POST /api/stripe/create-payment-intent` - Crear intent de pago
- `POST /api/pedidos/:id/confirmar-pago` - Confirmar pago

### Productos (Admin)
- `POST /api/admin/productos` - Crear producto
- `PUT /api/admin/productos/:id` - Actualizar producto
- `DELETE /api/admin/productos/:id` - Eliminar producto
- `POST /api/admin/upload-imagen` - Subir imagen

### Estadísticas (Admin)
- `GET /api/admin/estadisticas` - Estadísticas generales

## 🎨 Interfaz

### Tienda (index.html)
- ✅ Diseño original mantenido
- ✅ Modal de checkout mejorado con Stripe
- ✅ Botón de acceso al panel admin (solo para admins)

### Panel Admin (admin.html)
- ✨ Diseño moderno con sidebar
- 📊 Dashboard con estadísticas
- 🎯 Secciones organizadas
- 📱 Responsive design

## ⚠️ Notas Importantes

1. **Seguridad:**
   - Cambia las credenciales del admin después del primer uso
   - En producción, usa variables de entorno para las claves de Stripe
   - Implementa HTTPS en producción

2. **Stripe en Producción:**
   - Cambia a claves de producción
   - Configura webhooks para confirmación automática
   - Implementa manejo de errores robusto

3. **Stock:**
   - El stock se reduce automáticamente al confirmar pago
   - Verifica stock antes de procesar pedidos

4. **Estados de Pedido:**
   - pendiente → pagado → despachado → completado
   - Se puede cancelar si está en pendiente o pagado

## 🐛 Solución de Problemas

### "Token faltante" o "Acceso denegado"
- Cierra sesión y vuelve a iniciar sesión
- Verifica que el usuario sea administrador

### "Error al procesar pago"
- Verifica que uses la tarjeta de prueba correcta
- Asegúrate de que el servidor Flask esté corriendo
- Revisa la consola del navegador para más detalles

### Productos no aparecen en el panel
- Ejecuta `python seed_products.py`
- Verifica que la base de datos exista en `/instance/tienda_vestidos.db`

### Imágenes no se muestran
- Verifica que la carpeta `imagenes/` exista
- Asegúrate de que las rutas sean correctas

## 🚀 Iniciar el Servidor

```bash
python app.py
```

El servidor estará disponible en:
- **Tienda:** http://localhost:5000
- **Panel Admin:** http://localhost:5000/admin.html

## ✨ Características Adicionales

- 🔍 Búsqueda de productos
- 🛒 Carrito persistente (localStorage)
- 👤 Sistema de autenticación con JWT
- 📸 Subida de imágenes para productos
- 💰 Múltiples métodos de pago (Stripe)
- 📊 Estadísticas en tiempo real
- 🎨 Interfaz responsive y moderna

---

**¡Listo para usar! 🎉**

Si tienes alguna pregunta o necesitas ayuda adicional, no dudes en preguntar.
