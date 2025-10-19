// Configuración de la API
const API_URL = 'http://localhost:5000/api';

// Estado de la aplicación
let userToken = localStorage.getItem('userToken') || null;
let currentUser = JSON.parse(localStorage.getItem('currentUser')) || null;
let currentFilter = 'todos';
let categorias = [];
let productos = [];
let pedidos = [];

document.addEventListener('DOMContentLoaded', function() {
    // Verificar autenticación y permisos de admin
    if (!userToken || !currentUser || !currentUser.es_admin) {
        showNotification('Acceso denegado. Debes ser administrador.', 'error');
        setTimeout(() => {
            window.location.href = 'index.html';
        }, 2000);
        return;
    }
    
    // Event Listeners - Sidebar
    document.querySelectorAll('.menu-item').forEach(item => {
        item.addEventListener('click', function() {
            const section = this.getAttribute('data-section');
            switchSection(section);
        });
    });
    
    // Event Listeners - Logout
    document.getElementById('logoutBtn').addEventListener('click', logout);
    
    // Event Listeners - Filter buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            currentFilter = this.getAttribute('data-estado');
            cargarPedidos();
        });
    });
    
    // Event Listeners - Botones
    document.getElementById('btnNuevoProducto')?.addEventListener('click', abrirModalNuevoProducto);
    document.getElementById('btnNuevaCategoria')?.addEventListener('click', abrirModalNuevaCategoria);
    document.getElementById('btnCancelarProducto')?.addEventListener('click', cerrarModales);
    document.getElementById('btnCancelarCategoria')?.addEventListener('click', cerrarModales);
    
    // Event Listeners - Forms
    document.getElementById('productoForm').addEventListener('submit', guardarProducto);
    document.getElementById('categoriaForm').addEventListener('submit', guardarCategoria);
    
    // Event Listeners - Image Upload
    document.getElementById('productoImagen')?.addEventListener('change', previewImagen);
    document.getElementById('productoImagenUrl')?.addEventListener('input', function() {
        const url = this.value;
        if (url) {
            const preview = document.getElementById('imagen-preview');
            preview.innerHTML = `<img src="${url}" alt="Preview">`;
        }
    });
    
    // Event Listeners - Cerrar modales
    document.querySelectorAll('.close').forEach(btn => {
        btn.addEventListener('click', cerrarModales);
    });
    
    window.addEventListener('click', function(e) {
        if (e.target.classList.contains('modal')) {
            cerrarModales();
        }
    });
    
    // Cargar datos iniciales
    cargarEstadisticas();
    cargarCategorias();
});

// ==================== NAVEGACIÓN ====================

function switchSection(section) {
    // Actualizar sidebar
    document.querySelectorAll('.menu-item').forEach(item => {
        item.classList.remove('active');
        if (item.getAttribute('data-section') === section) {
            item.classList.add('active');
        }
    });
    
    // Actualizar secciones
    document.querySelectorAll('.admin-section').forEach(sec => {
        sec.classList.remove('active');
    });
    document.getElementById(`${section}-section`).classList.add('active');
    
    // Cargar datos según la sección
    switch(section) {
        case 'estadisticas':
            cargarEstadisticas();
            break;
        case 'pedidos':
            cargarPedidos();
            break;
        case 'productos':
            cargarProductos();
            break;
        case 'categorias':
            cargarCategorias();
            break;
    }
}

function logout() {
    localStorage.removeItem('userToken');
    localStorage.removeItem('currentUser');
    showNotification('Sesión cerrada exitosamente', 'success');
    setTimeout(() => {
        window.location.href = 'index.html';
    }, 1000);
}

// ==================== ESTADÍSTICAS ====================

async function cargarEstadisticas() {
    try {
        const response = await fetch(`${API_URL}/admin/estadisticas`, {
            headers: {
                'Authorization': `Bearer ${userToken}`
            }
        });
        
        if (!response.ok) throw new Error('Error al cargar estadísticas');
        
        const data = await response.json();
        
        document.getElementById('stat-pedidos-total').textContent = data.pedidos.total;
        document.getElementById('stat-pedidos-pendientes').textContent = data.pedidos.pendientes;
        document.getElementById('stat-pedidos-pagados').textContent = data.pedidos.pagados;
        document.getElementById('stat-pedidos-despachados').textContent = data.pedidos.despachados;
        document.getElementById('stat-ventas-total').textContent = `$${data.ventas.total.toLocaleString()} COP`;
        document.getElementById('stat-productos-total').textContent = data.productos.total;
        
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error al cargar estadísticas', 'error');
    }
}

// ==================== PEDIDOS ====================

async function cargarPedidos() {
    try {
        let url = `${API_URL}/admin/pedidos`;
        if (currentFilter !== 'todos') {
            url += `?estado=${currentFilter}`;
        }
        
        const response = await fetch(url, {
            headers: {
                'Authorization': `Bearer ${userToken}`
            }
        });
        
        if (!response.ok) throw new Error('Error al cargar pedidos');
        
        pedidos = await response.json();
        renderPedidos();
        
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error al cargar pedidos', 'error');
    }
}

function renderPedidos() {
    const container = document.getElementById('pedidos-container');
    
    if (pedidos.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-inbox"></i>
                <h3>No hay pedidos</h3>
                <p>No se encontraron pedidos con el filtro seleccionado</p>
            </div>
        `;
        return;
    }
    
    let html = '';
    pedidos.forEach(pedido => {
        html += `
            <div class="pedido-card estado-${pedido.estado}">
                <div class="pedido-header">
                    <div class="pedido-id">Pedido #${pedido.id}</div>
                    <div class="pedido-estado estado-${pedido.estado}">${pedido.estado}</div>
                </div>
                <div class="pedido-info">
                    <p><strong>Cliente:</strong> ${pedido.usuario.nombre}</p>
                    <p><strong>Email:</strong> ${pedido.usuario.email}</p>
                    <p><strong>Fecha:</strong> ${formatearFecha(pedido.fecha)}</p>
                    <p><strong>Items:</strong> ${pedido.items.length} producto(s)</p>
                </div>
                <div class="pedido-total">Total: $${pedido.total.toLocaleString()} COP</div>
                <div class="pedido-actions">
                    <button class="btn-primary" onclick="verDetallePedido(${pedido.id})">
                        <i class="fas fa-eye"></i> Ver Detalle
                    </button>
                    ${generarBotonesEstado(pedido)}
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

function generarBotonesEstado(pedido) {
    let botones = '';
    
    if (pedido.estado === 'pagado') {
        botones += `
            <button class="btn-success" onclick="cambiarEstadoPedido(${pedido.id}, 'despachado')">
                <i class="fas fa-truck"></i> Despachar
            </button>
        `;
    }
    
    if (pedido.estado === 'despachado') {
        botones += `
            <button class="btn-warning" onclick="cambiarEstadoPedido(${pedido.id}, 'completado')">
                <i class="fas fa-check"></i> Completar
            </button>
        `;
    }
    
    if (['pendiente', 'pagado'].includes(pedido.estado)) {
        botones += `
            <button class="btn-danger" onclick="cambiarEstadoPedido(${pedido.id}, 'cancelado')">
                <i class="fas fa-times"></i> Cancelar
            </button>
        `;
    }
    
    return botones;
}

async function cambiarEstadoPedido(pedidoId, nuevoEstado) {
    if (!confirm(`¿Estás seguro de cambiar el estado a "${nuevoEstado}"?`)) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/admin/pedidos/${pedidoId}/estado`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${userToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ estado: nuevoEstado })
        });
        
        if (!response.ok) throw new Error('Error al actualizar estado');
        
        showNotification('Estado actualizado exitosamente', 'success');
        cargarPedidos();
        cargarEstadisticas();
        
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error al actualizar estado', 'error');
    }
}

function verDetallePedido(pedidoId) {
    const pedido = pedidos.find(p => p.id === pedidoId);
    if (!pedido) return;
    
    let html = `
        <div class="pedido-detalle">
            <div class="pedido-info">
                <p><strong>Pedido #${pedido.id}</strong></p>
                <p><strong>Cliente:</strong> ${pedido.usuario.nombre} (${pedido.usuario.email})</p>
                <p><strong>Fecha:</strong> ${formatearFecha(pedido.fecha)}</p>
                <p><strong>Estado:</strong> <span class="pedido-estado estado-${pedido.estado}">${pedido.estado}</span></p>
                ${pedido.direccion_envio ? `<p><strong>Dirección:</strong> ${pedido.direccion_envio}</p>` : ''}
            </div>
            <h3 style="margin-top: 20px; margin-bottom: 15px;">Items del Pedido:</h3>
            <table class="admin-table">
                <thead>
                    <tr>
                        <th>Producto</th>
                        <th>Cantidad</th>
                        <th>Precio Unitario</th>
                        <th>Subtotal</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    pedido.items.forEach(item => {
        html += `
            <tr>
                <td>
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <img src="${item.producto.imagen_url}" class="producto-imagen">
                        <span>${item.producto.nombre}</span>
                    </div>
                </td>
                <td>${item.cantidad}</td>
                <td>$${item.precio_unitario.toLocaleString()} COP</td>
                <td>$${item.subtotal.toLocaleString()} COP</td>
            </tr>
        `;
    });
    
    html += `
                </tbody>
            </table>
            <div style="text-align: right; margin-top: 20px; font-size: 20px; font-weight: bold;">
                Total: $${pedido.total.toLocaleString()} COP
            </div>
        </div>
    `;
    
    document.getElementById('pedido-detalle-container').innerHTML = html;
    document.getElementById('pedidoModal').style.display = 'block';
}

// ==================== PRODUCTOS ====================

async function cargarProductos() {
    try {
        const response = await fetch(`${API_URL}/productos`);
        if (!response.ok) throw new Error('Error al cargar productos');
        
        productos = await response.json();
        renderProductos();
        
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error al cargar productos', 'error');
    }
}

function renderProductos() {
    const tbody = document.getElementById('productos-tbody');
    
    if (productos.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" style="text-align: center; padding: 40px;">
                    <div class="empty-state">
                        <i class="fas fa-box-open"></i>
                        <h3>No hay productos</h3>
                        <p>Agrega tu primer producto</p>
                    </div>
                </td>
            </tr>
        `;
        return;
    }
    
    let html = '';
    productos.forEach(producto => {
        const categoria = categorias.find(c => c.id === producto.categoria_id);
        const stockBadge = producto.stock === 0 ? 'badge-low' : producto.stock < 5 ? 'badge-medium' : 'badge-high';
        
        html += `
            <tr>
                <td>
                    <img src="${producto.imagen_url}" class="producto-imagen" alt="${producto.nombre}">
                </td>
                <td>${producto.nombre}</td>
                <td>${categoria ? categoria.nombre : 'Sin categoría'}</td>
                <td>$${producto.precio.toLocaleString()} COP</td>
                <td>
                    <span class="badge ${stockBadge}">${producto.stock}</span>
                </td>
                <td>
                    <div class="producto-actions">
                        <button class="btn-primary" onclick="editarProducto(${producto.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn-danger" onclick="eliminarProducto(${producto.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
    });
    
    tbody.innerHTML = html;
}

function abrirModalNuevoProducto() {
    document.getElementById('productoModalTitle').textContent = 'Nuevo Producto';
    document.getElementById('productoForm').reset();
    document.getElementById('productoId').value = '';
    document.getElementById('imagen-preview').innerHTML = '';
    cargarCategoriasSelect();
    document.getElementById('productoModal').style.display = 'block';
}

function editarProducto(productoId) {
    const producto = productos.find(p => p.id === productoId);
    if (!producto) return;
    
    document.getElementById('productoModalTitle').textContent = 'Editar Producto';
    document.getElementById('productoId').value = producto.id;
    document.getElementById('productoNombre').value = producto.nombre;
    document.getElementById('productoDescripcion').value = producto.descripcion || '';
    document.getElementById('productoPrecio').value = producto.precio;
    document.getElementById('productoStock').value = producto.stock;
    document.getElementById('productoTalla').value = producto.talla || '';
    document.getElementById('productoColor').value = producto.color || '';
    document.getElementById('productoImagenUrl').value = producto.imagen_url || '';
    document.getElementById('productoCategoria').value = producto.categoria_id || '';
    
    if (producto.imagen_url) {
        document.getElementById('imagen-preview').innerHTML = `<img src="${producto.imagen_url}" alt="Preview">`;
    }
    
    cargarCategoriasSelect();
    document.getElementById('productoModal').style.display = 'block';
}

async function guardarProducto(e) {
    e.preventDefault();
    
    const productoId = document.getElementById('productoId').value;
    const formData = {
        nombre: document.getElementById('productoNombre').value,
        descripcion: document.getElementById('productoDescripcion').value,
        precio: parseFloat(document.getElementById('productoPrecio').value),
        stock: parseInt(document.getElementById('productoStock').value),
        talla: document.getElementById('productoTalla').value,
        color: document.getElementById('productoColor').value,
        categoria_id: parseInt(document.getElementById('productoCategoria').value) || null,
        imagen_url: document.getElementById('productoImagenUrl').value
    };
    
    // Si hay una imagen seleccionada, subirla primero
    const fileInput = document.getElementById('productoImagen');
    if (fileInput.files.length > 0) {
        const imageUrl = await subirImagen(fileInput.files[0]);
        if (imageUrl) {
            formData.imagen_url = imageUrl;
        }
    }
    
    try {
        const url = productoId 
            ? `${API_URL}/admin/productos/${productoId}`
            : `${API_URL}/admin/productos`;
        
        const method = productoId ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Authorization': `Bearer ${userToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) throw new Error('Error al guardar producto');
        
        showNotification(
            productoId ? 'Producto actualizado exitosamente' : 'Producto creado exitosamente',
            'success'
        );
        
        cerrarModales();
        cargarProductos();
        cargarEstadisticas();
        
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error al guardar producto', 'error');
    }
}

async function eliminarProducto(productoId) {
    if (!confirm('¿Estás seguro de eliminar este producto?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/admin/productos/${productoId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${userToken}`
            }
        });
        
        if (!response.ok) throw new Error('Error al eliminar producto');
        
        showNotification('Producto eliminado exitosamente', 'success');
        cargarProductos();
        cargarEstadisticas();
        
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error al eliminar producto', 'error');
    }
}

async function subirImagen(file) {
    try {
        const formData = new FormData();
        formData.append('imagen', file);
        
        const response = await fetch(`${API_URL}/admin/upload-imagen`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${userToken}`
            },
            body: formData
        });
        
        if (!response.ok) throw new Error('Error al subir imagen');
        
        const data = await response.json();
        return data.imagen_url;
        
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error al subir imagen', 'error');
        return null;
    }
}

function previewImagen(e) {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById('imagen-preview').innerHTML = `<img src="${e.target.result}" alt="Preview">`;
            document.getElementById('productoImagenUrl').value = '';
        };
        reader.readAsDataURL(file);
    }
}

// ==================== CATEGORÍAS ====================

async function cargarCategorias() {
    try {
        const response = await fetch(`${API_URL}/categorias`);
        if (!response.ok) throw new Error('Error al cargar categorías');
        
        categorias = await response.json();
        renderCategorias();
        
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error al cargar categorías', 'error');
    }
}

function renderCategorias() {
    const container = document.getElementById('categorias-container');
    
    if (categorias.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-tags"></i>
                <h3>No hay categorías</h3>
                <p>Crea tu primera categoría</p>
            </div>
        `;
        return;
    }
    
    let html = '';
    categorias.forEach(categoria => {
        html += `
            <div class="categoria-card">
                <div class="categoria-icon">
                    <i class="fas fa-tag"></i>
                </div>
                <div class="categoria-nombre">${categoria.nombre}</div>
                <div class="categoria-descripcion">${categoria.descripcion || 'Sin descripción'}</div>
                <div class="categoria-productos">${categoria.num_productos} producto(s)</div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

function cargarCategoriasSelect() {
    const select = document.getElementById('productoCategoria');
    select.innerHTML = '<option value="">Seleccionar categoría</option>';
    
    categorias.forEach(categoria => {
        select.innerHTML += `<option value="${categoria.id}">${categoria.nombre}</option>`;
    });
}

function abrirModalNuevaCategoria() {
    document.getElementById('categoriaForm').reset();
    document.getElementById('categoriaModal').style.display = 'block';
}

async function guardarCategoria(e) {
    e.preventDefault();
    
    const formData = {
        nombre: document.getElementById('categoriaNombre').value,
        descripcion: document.getElementById('categoriaDescripcion').value
    };
    
    try {
        const response = await fetch(`${API_URL}/categorias`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${userToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) throw new Error('Error al crear categoría');
        
        showNotification('Categoría creada exitosamente', 'success');
        cerrarModales();
        cargarCategorias();
        
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error al crear categoría', 'error');
    }
}

// ==================== UTILIDADES ====================

function cerrarModales() {
    document.querySelectorAll('.modal').forEach(modal => {
        modal.style.display = 'none';
    });
}

function formatearFecha(fechaString) {
    const fecha = new Date(fechaString);
    return fecha.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#26de81' : '#ff4757'};
        color: white;
        padding: 15px 25px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 10000;
        transform: translateX(400px);
        transition: transform 0.3s ease;
        max-width: 300px;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    setTimeout(() => {
        notification.style.transform = 'translateX(400px)';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}
