# ✅ Checklist de Pruebas - GLAM RENT

## 🧪 Pruebas Recomendadas

### 1. Iniciar el Servidor
```bash
./start_server.sh
# o
python3 app.py
```

**Verificar:**
- [ ] El servidor inicia sin errores
- [ ] Muestra el mensaje "Servidor iniciado en http://localhost:5000"

---

### 2. Pruebas de la Tienda (Cliente)

#### 2.1. Navegación Básica
- [ ] Abrir http://localhost:5000
- [ ] Verificar que se vean todos los productos
- [ ] Verificar que las imágenes se carguen correctamente
- [ ] Hacer scroll por todas las secciones

#### 2.2. Registro e Inicio de Sesión
- [ ] Click en "Login"
- [ ] Click en "¿No tienes cuenta? Regístrate aquí"
- [ ] Registrar nuevo usuario (usa tu email)
- [ ] Cerrar sesión
- [ ] Iniciar sesión con el usuario creado
- [ ] Verificar que aparezca tu nombre en el header

#### 2.3. Carrito de Compras
- [ ] Agregar varios productos al carrito (click en el precio)
- [ ] Verificar que el contador del carrito se actualice
- [ ] Abrir el carrito
- [ ] Cambiar cantidades de productos (+/-)
- [ ] Eliminar un producto del carrito
- [ ] Verificar que el total se calcule correctamente

#### 2.4. Búsqueda de Productos
- [ ] Click en el icono de búsqueda
- [ ] Buscar "corsé" o "vestido"
- [ ] Verificar que aparezcan resultados
- [ ] Agregar producto desde búsqueda al carrito

#### 2.5. Proceso de Pago (¡IMPORTANTE!)
- [ ] Con productos en el carrito, click en "Proceder al Pago"
- [ ] Ingresar dirección de envío
- [ ] Ingresar tarjeta de prueba:
  - Número: `4242 4242 4242 4242`
  - Fecha: `12/25`
  - CVV: `123`
- [ ] Click en "Pagar Ahora"
- [ ] Esperar confirmación de pago
- [ ] Verificar que el carrito se vacíe
- [ ] Verificar mensaje de éxito

---

### 3. Pruebas del Panel de Administración

#### 3.1. Acceso al Panel
- [ ] Cerrar sesión si estás con usuario normal
- [ ] Iniciar sesión con:
  - Email: `admin@glamrent.com`
  - Contraseña: `admin123`
- [ ] Verificar que aparezca corona 👑 en el nombre
- [ ] Verificar que aparezca botón "Panel Admin"
- [ ] Click en "Panel Admin" o ir a http://localhost:5000/admin.html

#### 3.2. Dashboard de Estadísticas
- [ ] Verificar que aparezcan las tarjetas de estadísticas
- [ ] Verificar números:
  - Total Pedidos
  - Pedidos Pendientes/Pagados/Despachados
  - Total Ventas
  - Total Productos

#### 3.3. Gestión de Pedidos
- [ ] Click en "Pedidos" en el sidebar
- [ ] Verificar que aparezca el pedido que creaste antes
- [ ] Click en "Ver Detalle" de un pedido
- [ ] Verificar información completa del pedido
- [ ] Cerrar modal
- [ ] Si el pedido está "pagado", click en "Despachar"
- [ ] Verificar que el estado cambie a "despachado"
- [ ] Filtrar pedidos por estado (botones: Todos, Pendientes, etc.)

#### 3.4. Gestión de Productos
- [ ] Click en "Productos" en el sidebar
- [ ] Verificar lista de productos en tabla
- [ ] **Editar Producto:**
  - Click en el botón de editar (lápiz) de un producto
  - Cambiar el stock (ej: de 10 a 8)
  - Guardar cambios
  - Verificar que se actualice en la tabla
- [ ] **Crear Nuevo Producto:**
  - Click en "Nuevo Producto"
  - Llenar todos los campos:
    - Nombre: "Vestido de Prueba"
    - Categoría: Seleccionar una
    - Precio: 150000
    - Stock: 5
    - Talla: "M"
    - Color: "Negro"
  - Opción A: Subir una imagen desde tu computadora
  - Opción B: Usar URL: `imagenes/vestido 1.png`
  - Click en "Guardar Producto"
  - Verificar que aparezca en la lista
- [ ] **Eliminar Producto:**
  - Click en eliminar (🗑️) en el producto de prueba
  - Confirmar eliminación
  - Verificar que desaparezca

#### 3.5. Gestión de Categorías
- [ ] Click en "Categorías" en el sidebar
- [ ] Verificar categorías existentes
- [ ] Click en "Nueva Categoría"
- [ ] Crear nueva categoría:
  - Nombre: "Accesorios"
  - Descripción: "Accesorios para complementar tu look"
- [ ] Guardar y verificar que aparezca

---

### 4. Pruebas de Integración

#### 4.1. Flujo Completo Cliente → Admin
1. **Como Cliente:**
   - [ ] Registrar nuevo usuario
   - [ ] Agregar 2-3 productos al carrito
   - [ ] Procesar pago con Stripe
   - [ ] Verificar confirmación

2. **Como Admin:**
   - [ ] Cerrar sesión
   - [ ] Iniciar sesión como admin
   - [ ] Ir al panel de administración
   - [ ] Verificar que aparezca el nuevo pedido
   - [ ] Ver detalles del pedido
   - [ ] Cambiar estado a "despachado"
   - [ ] Verificar que las estadísticas se actualicen

#### 4.2. Verificar Stock
- [ ] Como admin, ver el stock de un producto (ej: 10 unidades)
- [ ] Como cliente, hacer un pedido con 2 unidades de ese producto
- [ ] Pagar el pedido
- [ ] Como admin, verificar que el stock se redujo a 8 unidades

#### 4.3. Productos Sin Stock
- [ ] Como admin, editar un producto y poner stock en 0
- [ ] Verificar que el producto muestre badge rojo en la tabla
- [ ] Como cliente, intentar agregarlo al carrito (debe funcionar)
- [ ] Intentar hacer checkout (debe mostrar error de stock)

---

### 5. Pruebas de UI/UX

#### 5.1. Responsive Design
- [ ] Abrir en modo móvil (DevTools → Toggle device toolbar)
- [ ] Verificar que la tienda se vea bien en móvil
- [ ] Verificar que el panel admin se adapte
- [ ] Verificar que los modales sean usables en móvil

#### 5.2. Notificaciones
- [ ] Verificar que aparezcan notificaciones al:
  - Agregar producto al carrito
  - Iniciar/cerrar sesión
  - Completar pago
  - Editar/crear/eliminar productos (admin)
  - Cambiar estado de pedido (admin)

#### 5.3. Modales
- [ ] Verificar que todos los modales se puedan cerrar con la X
- [ ] Verificar que se puedan cerrar haciendo click fuera
- [ ] Verificar que no se pueda hacer scroll cuando un modal está abierto

---

### 6. Pruebas de Seguridad Básicas

#### 6.1. Protección de Rutas Admin
- [ ] Cerrar sesión
- [ ] Intentar acceder a http://localhost:5000/admin.html
- [ ] Verificar que redirija a la página principal con mensaje de error

#### 6.2. Tokens
- [ ] Iniciar sesión
- [ ] Abrir DevTools → Application → Local Storage
- [ ] Verificar que exista `userToken`
- [ ] Cerrar sesión
- [ ] Verificar que el token se elimine

---

### 7. Pruebas de Errores

#### 7.1. Errores de Login
- [ ] Intentar login con email inexistente
- [ ] Intentar login con contraseña incorrecta
- [ ] Verificar mensajes de error apropiados

#### 7.2. Errores de Pago
- [ ] Intentar pagar con carrito vacío
- [ ] Intentar pagar sin estar logueado
- [ ] Intentar pagar con número de tarjeta inválido: `4000000000000002`
- [ ] Verificar mensajes de error

#### 7.3. Errores de Formularios
- [ ] Intentar crear producto sin nombre
- [ ] Intentar crear producto sin precio
- [ ] Verificar validación de campos requeridos

---

## 📊 Resultados Esperados

### ✅ Todo Debe Funcionar:
- ✓ Registro e inicio de sesión
- ✓ Agregar productos al carrito
- ✓ Procesar pagos con Stripe
- ✓ Ver pedidos como cliente
- ✓ Panel de administración completo
- ✓ Gestión de pedidos (cambiar estados)
- ✓ Gestión de productos (crear, editar, eliminar)
- ✓ Subida de imágenes
- ✓ Gestión de categorías
- ✓ Reducción automática de stock
- ✓ Estadísticas en tiempo real
- ✓ Notificaciones de acciones
- ✓ Diseño responsive
- ✓ Protección de rutas admin

---

## 🐛 Si Encuentras Errores

### Problemas Comunes:

1. **"No module named 'stripe'"**
   ```bash
   pip3 install stripe
   ```

2. **"Token inválido" o "Acceso denegado"**
   - Cierra sesión y vuelve a iniciar sesión
   - Borra localStorage del navegador

3. **Imágenes no se muestran**
   - Verifica que la carpeta `imagenes/` exista
   - Verifica las rutas de las imágenes

4. **Error al subir imagen**
   - Verifica que la carpeta `imagenes/` tenga permisos de escritura
   - Usa imágenes menores a 16MB

5. **Base de datos corrupta**
   ```bash
   rm -f instance/tienda_vestidos.db
   python3 init_admin.py
   python3 seed_products.py
   ```

---

## 📸 Screenshots Recomendados

Para documentar, toma screenshots de:
1. ✅ Página principal de la tienda
2. ✅ Modal de checkout con Stripe
3. ✅ Confirmación de pago exitoso
4. ✅ Panel de administración (dashboard)
5. ✅ Gestión de pedidos
6. ✅ Formulario de crear/editar producto
7. ✅ Vista responsive en móvil

---

**¡Buena suerte con las pruebas! 🚀**
