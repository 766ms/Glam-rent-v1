// Configuración de la API
const API_URL = 'http://localhost:5000/api';

// Estado de la aplicación
let userToken = localStorage.getItem('userToken') || null;
let currentUser = JSON.parse(localStorage.getItem('currentUser')) || null;
let cart = JSON.parse(localStorage.getItem('cart')) || [];

// Stripe
let stripe;
let elements;
let cardElement;
let currentPedidoId = null;

// Variables de modales
let isLoginMode = true;

document.addEventListener('DOMContentLoaded', async function() {
    // Elementos del DOM
    const loginBtn = document.getElementById('loginBtn');
    const cartBtn = document.getElementById('cartBtn');
    const searchBtn = document.getElementById('searchBtn');
    const loginModal = document.getElementById('loginModal');
    const cartModal = document.getElementById('cartModal');
    const searchModal = document.getElementById('searchModal');
    const closeButtons = document.querySelectorAll('.close');
    const authForm = document.getElementById('authForm');
    const switchAuthMode = document.getElementById('switchAuthMode');
    const contactForm = document.getElementById('contactForm');
    
    // Inicializar Stripe
    await initStripe();
    
    // Actualizar UI basado en autenticación
    updateUIBasedOnAuth();
    updateCartCount();
    
    // Event Listeners - Login
    loginBtn.addEventListener('click', function(e) {
        e.preventDefault();
        if (userToken) {
            logout();
        } else {
            openLoginModal();
        }
    });
    
    // Event Listeners - Carrito
    cartBtn.addEventListener('click', function(e) {
        e.preventDefault();
        openCartModal();
    });
    
    // Event Listeners - Búsqueda
    searchBtn.addEventListener('click', function(e) {
        e.preventDefault();
        openSearchModal();
    });
    
    document.getElementById('searchButton').addEventListener('click', performSearch);
    document.getElementById('searchInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            performSearch();
        }
    });
    
    // Event Listeners - Cerrar modales
    closeButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            closeAllModals();
        });
    });
    
    document.getElementById('closeCheckout')?.addEventListener('click', closeAllModals);
    
    window.addEventListener('click', function(e) {
        if (e.target.classList.contains('modal')) {
            closeAllModals();
        }
    });
    
    // Event Listeners - Auth Form
    authForm.addEventListener('submit', function(e) {
        e.preventDefault();
        if (isLoginMode) {
            handleLogin();
        } else {
            handleRegister();
        }
    });
    
    switchAuthMode.querySelector('a').addEventListener('click', function(e) {
        e.preventDefault();
        toggleAuthMode();
    });
    
    // Event Listeners - Contact Form (Newsletter)
    contactForm.addEventListener('submit', function(e) {
        e.preventDefault();
        handleNewsletter();
    });
    
    // Event Listeners - Productos
    document.querySelectorAll('.product-price').forEach(button => {
        button.addEventListener('click', function() {
            const productCard = this.closest('.product-card');
            const productId = productCard.getAttribute('data-product-id');
            const productName = productCard.querySelector('.product-name').textContent.trim();
            const productPrice = parseInt(this.getAttribute('data-price'));
            const productImage = productCard.querySelector('img').src;
            
            addToCart({
                id: productId,
                name: productName,
                price: productPrice,
                image: productImage,
                quantity: 1
            });
        });
    });
    
    // Smooth scroll
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href !== '#') {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
    
    // Animación del header al hacer scroll
    let lastScrollTop = 0;
    window.addEventListener('scroll', function() {
        const header = document.querySelector('.header');
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        if (scrollTop > lastScrollTop && scrollTop > 100) {
            header.style.transform = 'translateY(-100%)';
        } else {
            header.style.transform = 'translateY(0)';
        }
        lastScrollTop = scrollTop;
    });
});

// ==================== AUTENTICACIÓN ====================

async function handleLogin() {
    const email = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    if (!email || !password) {
        showNotification('Por favor, completa todos los campos.', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            userToken = data.token;
            currentUser = data.usuario;
            localStorage.setItem('userToken', userToken);
            localStorage.setItem('currentUser', JSON.stringify(currentUser));
            
            showNotification(`¡Bienvenido/a ${currentUser.nombre}!`, 'success');
            closeAllModals();
            updateUIBasedOnAuth();
        } else {
            showNotification(data.mensaje || 'Error al iniciar sesión', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error de conexión. Verifica que el servidor esté corriendo.', 'error');
    }
}

async function handleRegister() {
    const nombre = document.getElementById('registerName').value;
    const email = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    if (!nombre || !email || !password) {
        showNotification('Por favor, completa todos los campos.', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/registro`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ nombre, email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showNotification('¡Registro exitoso! Ahora puedes iniciar sesión.', 'success');
            toggleAuthMode();
            document.getElementById('authForm').reset();
        } else {
            showNotification(data.mensaje || 'Error al registrarse', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error de conexión. Verifica que el servidor esté corriendo.', 'error');
    }
}

function logout() {
    userToken = null;
    currentUser = null;
    localStorage.removeItem('userToken');
    localStorage.removeItem('currentUser');
    showNotification('Sesión cerrada exitosamente', 'success');
    updateUIBasedOnAuth();
}

function updateUIBasedOnAuth() {
    const loginBtn = document.getElementById('loginBtn');
    if (userToken && currentUser) {
        let text = `${currentUser.nombre}`;
        if (currentUser.es_admin) {
            text += ' 👑';
        }
        text += ' | Salir';
        loginBtn.textContent = text;
        
        // Si es admin, agregar botón para ir al panel
        if (currentUser.es_admin && !document.getElementById('adminPanelBtn')) {
            const adminBtn = document.createElement('a');
            adminBtn.id = 'adminPanelBtn';
            adminBtn.href = 'admin.html';
            adminBtn.className = 'nav-link';
            adminBtn.innerHTML = '<i class="fas fa-cog"></i> Panel Admin';
            adminBtn.style.color = '#F0C5CE';
            adminBtn.style.fontWeight = 'bold';
            
            const navMenu = document.querySelector('.nav-menu');
            navMenu.insertBefore(adminBtn, loginBtn);
        }
    } else {
        loginBtn.textContent = 'Login';
        // Remover botón de admin si existe
        const adminBtn = document.getElementById('adminPanelBtn');
        if (adminBtn) {
            adminBtn.remove();
        }
    }
}

function toggleAuthMode() {
    isLoginMode = !isLoginMode;
    const modalTitle = document.getElementById('modalTitle');
    const authSubmitBtn = document.getElementById('authSubmitBtn');
    const switchAuthMode = document.getElementById('switchAuthMode');
    const nameGroup = document.getElementById('nameGroup');
    
    if (isLoginMode) {
        modalTitle.textContent = 'INICIAR SESIÓN';
        authSubmitBtn.textContent = 'Ingresar';
        switchAuthMode.innerHTML = '¿No tienes una cuenta? <a href="#">Regístrate aquí</a>';
        nameGroup.style.display = 'none';
        document.getElementById('registerName').removeAttribute('required');
    } else {
        modalTitle.textContent = 'REGISTRARSE';
        authSubmitBtn.textContent = 'Registrarse';
        switchAuthMode.innerHTML = '¿Ya tienes cuenta? <a href="#">Inicia sesión aquí</a>';
        nameGroup.style.display = 'block';
        document.getElementById('registerName').setAttribute('required', 'required');
    }
    
    document.getElementById('authForm').reset();
    
    // Re-asignar evento al nuevo enlace
    switchAuthMode.querySelector('a').addEventListener('click', function(e) {
        e.preventDefault();
        toggleAuthMode();
    });
}

// ==================== CARRITO ====================

function addToCart(product) {
    const existingProduct = cart.find(item => item.id === product.id);
    
    if (existingProduct) {
        existingProduct.quantity += 1;
        showNotification('Cantidad actualizada en el carrito', 'success');
    } else {
        cart.push(product);
        showNotification(`"${product.name}" añadido al carrito exitosamente! 🛍️`, 'success');
    }
    
    saveCart();
    updateCartCount();
}

function removeFromCart(productId) {
    cart = cart.filter(item => item.id !== productId);
    saveCart();
    updateCartCount();
    renderCart();
    showNotification('Producto eliminado del carrito', 'success');
}

function updateQuantity(productId, quantity) {
    const product = cart.find(item => item.id === productId);
    if (product) {
        if (quantity <= 0) {
            removeFromCart(productId);
        } else {
            product.quantity = quantity;
            saveCart();
            renderCart();
        }
    }
}

function saveCart() {
    localStorage.setItem('cart', JSON.stringify(cart));
}

function updateCartCount() {
    const cartCount = document.getElementById('cartCount');
    const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
    cartCount.textContent = totalItems;
}

function renderCart() {
    const cartItems = document.getElementById('cartItems');
    const cartTotal = document.getElementById('cartTotal');
    
    if (cart.length === 0) {
        cartItems.innerHTML = '<p class="empty-cart">Tu carrito está vacío</p>';
        cartTotal.textContent = '$0 COP';
        return;
    }
    
    let total = 0;
    let html = '';
    
    cart.forEach(item => {
        const subtotal = item.price * item.quantity;
        total += subtotal;
        
        html += `
            <div class="cart-item">
                <img src="${item.image}" alt="${item.name}">
                <div class="cart-item-details">
                    <h4>${item.name}</h4>
                    <p>$${item.price.toLocaleString()} COP</p>
                </div>
                <div class="cart-item-quantity">
                    <button onclick="updateQuantity('${item.id}', ${item.quantity - 1})">-</button>
                    <span>${item.quantity}</span>
                    <button onclick="updateQuantity('${item.id}', ${item.quantity + 1})">+</button>
                </div>
                <div class="cart-item-subtotal">
                    <p>$${subtotal.toLocaleString()} COP</p>
                    <button onclick="removeFromCart('${item.id}')" class="remove-btn">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `;
    });
    
    cartItems.innerHTML = html;
    cartTotal.textContent = `$${total.toLocaleString()} COP`;
}

async function checkout() {
    if (cart.length === 0) {
        showNotification('Tu carrito está vacío', 'error');
        return;
    }
    
    if (!userToken) {
        showNotification('Debes iniciar sesión para proceder al pago', 'error');
        closeAllModals();
        openLoginModal();
        return;
    }
    
    // Abrir modal de checkout
    closeAllModals();
    openCheckoutModal();
}

async function openCheckoutModal() {
    // Renderizar resumen del pedido
    renderCheckoutSummary();
    
    document.getElementById('checkoutModal').style.display = 'block';
    document.body.style.overflow = 'hidden';
}

function renderCheckoutSummary() {
    const checkoutItems = document.getElementById('checkout-items');
    const checkoutTotal = document.getElementById('checkout-total-amount');
    
    let total = 0;
    let html = '';
    
    cart.forEach(item => {
        const subtotal = item.price * item.quantity;
        total += subtotal;
        
        html += `
            <div class="checkout-item">
                <span>${item.name} x ${item.quantity}</span>
                <span>$${subtotal.toLocaleString()} COP</span>
            </div>
        `;
    });
    
    checkoutItems.innerHTML = html;
    checkoutTotal.textContent = `$${total.toLocaleString()} COP`;
}

async function initStripe() {
    try {
        // Obtener clave pública de Stripe
        const response = await fetch(`${API_URL}/stripe/config`);
        const { publicKey } = await response.json();
        
        stripe = Stripe(publicKey);
        elements = stripe.elements();
        
        // Crear y montar Card Element
        cardElement = elements.create('card', {
            style: {
                base: {
                    fontSize: '16px',
                    color: '#333',
                    '::placeholder': {
                        color: '#aab7c4',
                    },
                },
                invalid: {
                    color: '#ff4757',
                },
            },
        });
        
        // Esperar a que el DOM esté listo
        setTimeout(() => {
            const cardElementContainer = document.getElementById('card-element');
            if (cardElementContainer) {
                cardElement.mount('#card-element');
                
                // Manejar errores del card element
                cardElement.on('change', function(event) {
                    const displayError = document.getElementById('card-errors');
                    if (event.error) {
                        displayError.textContent = event.error.message;
                    } else {
                        displayError.textContent = '';
                    }
                });
            }
        }, 100);
        
        // Event listener del formulario de pago
        const paymentForm = document.getElementById('payment-form');
        if (paymentForm) {
            paymentForm.addEventListener('submit', handlePayment);
        }
        
    } catch (error) {
        console.error('Error al inicializar Stripe:', error);
    }
}

async function handlePayment(e) {
    e.preventDefault();
    
    const submitButton = document.getElementById('submit-payment');
    const buttonText = document.getElementById('button-text');
    const spinner = document.getElementById('spinner');
    
    // Deshabilitar botón y mostrar spinner
    submitButton.disabled = true;
    buttonText.textContent = 'Procesando...';
    spinner.classList.remove('hidden');
    
    try {
        // 1. Crear pedido en el backend
        const direccion = document.getElementById('direccion').value;
        
        const pedidoResponse = await fetch(`${API_URL}/pedidos`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${userToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ direccion_envio: direccion })
        });
        
        if (!pedidoResponse.ok) {
            const errorData = await pedidoResponse.json();
            throw new Error(errorData.mensaje || 'Error al crear pedido');
        }
        
        const pedidoData = await pedidoResponse.json();
        currentPedidoId = pedidoData.pedido_id;
        
        // 2. Crear Payment Intent
        const paymentIntentResponse = await fetch(`${API_URL}/stripe/create-payment-intent`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${userToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ pedido_id: currentPedidoId })
        });
        
        if (!paymentIntentResponse.ok) {
            throw new Error('Error al crear payment intent');
        }
        
        const { clientSecret } = await paymentIntentResponse.json();
        
        // 3. Confirmar pago con Stripe
        const { error, paymentIntent } = await stripe.confirmCardPayment(clientSecret, {
            payment_method: {
                card: cardElement,
                billing_details: {
                    name: currentUser.nombre,
                    email: currentUser.email,
                },
            },
        });
        
        if (error) {
            throw new Error(error.message);
        }
        
        if (paymentIntent.status === 'succeeded') {
            // 4. Confirmar pago en el backend
            await fetch(`${API_URL}/pedidos/${currentPedidoId}/confirmar-pago`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${userToken}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ payment_intent_id: paymentIntent.id })
            });
            
            // 5. Limpiar carrito local
            cart = [];
            saveCart();
            updateCartCount();
            
            // 6. Mostrar éxito
            showNotification('¡Pago exitoso! Tu pedido ha sido procesado. 🎉', 'success');
            closeAllModals();
            
            // Reset form
            document.getElementById('payment-form').reset();
            cardElement.clear();
        }
        
    } catch (error) {
        console.error('Error:', error);
        showNotification(error.message || 'Error al procesar el pago', 'error');
        
    } finally {
        // Rehabilitar botón
        submitButton.disabled = false;
        buttonText.textContent = 'Pagar Ahora';
        spinner.classList.add('hidden');
    }
}

document.getElementById('checkoutBtn')?.addEventListener('click', checkout);

// ==================== BÚSQUEDA ====================

async function performSearch() {
    const searchInput = document.getElementById('searchInput').value.trim();
    const searchResults = document.getElementById('searchResults');
    
    if (!searchInput) {
        showNotification('Por favor ingresa un término de búsqueda', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/productos/buscar?q=${encodeURIComponent(searchInput)}`);
        const products = await response.json();
        
        if (products.length === 0) {
            searchResults.innerHTML = '<p class="no-results">No se encontraron productos</p>';
            return;
        }
        
        let html = '<div class="search-results-grid">';
        products.forEach(product => {
            html += `
                <div class="product-card">
                    <img src="${product.imagen_url}" alt="${product.nombre}">
                    <h3 class="product-name">${product.nombre}</h3>
                    <p class="product-description">${product.descripcion}</p>
                    <button class="product-price" onclick="addToCartFromSearch('${product.id}', '${product.nombre}', ${product.precio}, '${product.imagen_url}')">
                        ${product.precio.toLocaleString()} COP
                    </button>
                </div>
            `;
        });
        html += '</div>';
        
        searchResults.innerHTML = html;
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error al buscar productos', 'error');
    }
}

function addToCartFromSearch(id, name, price, image) {
    addToCart({
        id: id,
        name: name,
        price: price,
        image: image,
        quantity: 1
    });
}

// ==================== NEWSLETTER ====================

function handleNewsletter() {
    const email = document.getElementById('email').value;
    const name = document.getElementById('name').value;
    
    if (!email || !name) {
        showNotification('Por favor, completa todos los campos.', 'error');
        return;
    }
    
    // Aquí podrías hacer una llamada a tu API para guardar el newsletter
    showNotification('¡Gracias por suscribirte! Te mantendremos informado. 📧', 'success');
    document.getElementById('contactForm').reset();
}

// ==================== MODALES ====================

function openLoginModal() {
    document.getElementById('loginModal').style.display = 'block';
    document.body.style.overflow = 'hidden';
}

function openCartModal() {
    renderCart();
    document.getElementById('cartModal').style.display = 'block';
    document.body.style.overflow = 'hidden';
}

function openSearchModal() {
    document.getElementById('searchModal').style.display = 'block';
    document.body.style.overflow = 'hidden';
    document.getElementById('searchInput').focus();
}

function closeAllModals() {
    document.querySelectorAll('.modal').forEach(modal => {
        modal.style.display = 'none';
    });
    document.body.style.overflow = 'auto';
}

// ==================== NOTIFICACIONES ====================

function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#F0C5CE' : '#ff4757'};
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