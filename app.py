from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import jwt
import datetime
from functools import wraps
import stripe
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'glam-rent-cartagena-2024-super-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tienda_vestidos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'imagenes'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Configuración de Stripe (usa tu clave secreta de prueba)
# Para seguridad, usa variables de entorno en producción
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_tu_clave_secreta_aqui')

CORS(app)
db = SQLAlchemy(app)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Modelos de Base de Datos
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    es_admin = db.Column(db.Boolean, default=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    carritos = db.relationship('Carrito', backref='usuario', lazy=True, cascade='all, delete-orphan')
    pedidos = db.relationship('Pedido', backref='usuario', lazy=True)

class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    descripcion = db.Column(db.Text)
    productos = db.relationship('Producto', backref='categoria', lazy=True)

class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    precio = db.Column(db.Float, nullable=False)
    talla = db.Column(db.String(10))
    color = db.Column(db.String(50))
    imagen_url = db.Column(db.String(300))
    stock = db.Column(db.Integer, default=0)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'))

class Carrito(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    cantidad = db.Column(db.Integer, default=1)
    fecha_agregado = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    producto = db.relationship('Producto')

class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    fecha_pedido = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    total = db.Column(db.Float, nullable=False)
    estado = db.Column(db.String(50), default='pendiente')  # pendiente, pagado, despachado, completado, cancelado
    stripe_payment_id = db.Column(db.String(200))
    direccion_envio = db.Column(db.Text)
    items = db.relationship('ItemPedido', backref='pedido', lazy=True, cascade='all, delete-orphan')

class ItemPedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedido.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)
    producto = db.relationship('Producto')

# Decorador para verificar token
def token_requerido(f):
    @wraps(f)
    def decorador(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'mensaje': 'Token faltante'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token.split(' ')[1]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            usuario_actual = Usuario.query.get(data['usuario_id'])
            if not usuario_actual:
                return jsonify({'mensaje': 'Usuario no encontrado'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'mensaje': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'mensaje': 'Token inválido'}), 401
        except Exception as e:
            return jsonify({'mensaje': 'Error al verificar token'}), 401
        
        return f(usuario_actual, *args, **kwargs)
    
    return decorador

# Decorador para verificar que el usuario es admin
def admin_requerido(f):
    @wraps(f)
    def decorador(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'mensaje': 'Token faltante'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token.split(' ')[1]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            usuario_actual = Usuario.query.get(data['usuario_id'])
            if not usuario_actual:
                return jsonify({'mensaje': 'Usuario no encontrado'}), 401
            if not usuario_actual.es_admin:
                return jsonify({'mensaje': 'Acceso denegado. Se requieren permisos de administrador'}), 403
        except jwt.ExpiredSignatureError:
            return jsonify({'mensaje': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'mensaje': 'Token inválido'}), 401
        except Exception as e:
            return jsonify({'mensaje': 'Error al verificar token'}), 401
        
        return f(usuario_actual, *args, **kwargs)
    
    return decorador

# Rutas de Autenticación
@app.route('/api/registro', methods=['POST'])
def registro():
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password') or not data.get('nombre'):
            return jsonify({'mensaje': 'Faltan campos requeridos'}), 400
        
        if Usuario.query.filter_by(email=data['email']).first():
            return jsonify({'mensaje': 'El email ya está registrado'}), 400
        
        password_hash = generate_password_hash(data['password'])
        
        nuevo_usuario = Usuario(
            nombre=data['nombre'],
            email=data['email'],
            password=password_hash
        )
        
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        return jsonify({'mensaje': 'Usuario registrado exitosamente'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'mensaje': f'Error al registrar usuario: {str(e)}'}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'mensaje': 'Email y contraseña son requeridos'}), 400
        
        usuario = Usuario.query.filter_by(email=data['email']).first()
        
        if not usuario or not check_password_hash(usuario.password, data['password']):
            return jsonify({'mensaje': 'Email o contraseña incorrectos'}), 401
        
        token = jwt.encode({
            'usuario_id': usuario.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm="HS256")
        
        return jsonify({
            'token': token,
            'usuario': {
                'id': usuario.id,
                'nombre': usuario.nombre,
                'email': usuario.email,
                'es_admin': usuario.es_admin
            }
        }), 200
    except Exception as e:
        return jsonify({'mensaje': f'Error al iniciar sesión: {str(e)}'}), 500

# Rutas de Productos
@app.route('/api/productos', methods=['GET'])
def obtener_productos():
    try:
        productos = Producto.query.all()
        
        resultado = []
        for p in productos:
            resultado.append({
                'id': p.id,
                'nombre': p.nombre,
                'descripcion': p.descripcion,
                'precio': p.precio,
                'talla': p.talla,
                'color': p.color,
                'imagen_url': p.imagen_url,
                'stock': p.stock
            })
        
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'mensaje': f'Error al obtener productos: {str(e)}'}), 500

@app.route('/api/productos/buscar', methods=['GET'])
def buscar_productos():
    try:
        query = request.args.get('q', '').lower()
        
        if not query:
            return jsonify([]), 200
        
        productos = Producto.query.filter(
            db.or_(
                Producto.nombre.ilike(f'%{query}%'),
                Producto.descripcion.ilike(f'%{query}%'),
                Producto.color.ilike(f'%{query}%')
            )
        ).all()
        
        resultado = []
        for p in productos:
            resultado.append({
                'id': p.id,
                'nombre': p.nombre,
                'descripcion': p.descripcion,
                'precio': p.precio,
                'talla': p.talla,
                'color': p.color,
                'imagen_url': p.imagen_url,
                'stock': p.stock
            })
        
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'mensaje': f'Error al buscar productos: {str(e)}'}), 500

@app.route('/api/productos/<int:id>', methods=['GET'])
def obtener_producto(id):
    try:
        producto = Producto.query.get_or_404(id)
        
        return jsonify({
            'id': producto.id,
            'nombre': producto.nombre,
            'descripcion': producto.descripcion,
            'precio': producto.precio,
            'talla': producto.talla,
            'color': producto.color,
            'imagen_url': producto.imagen_url,
            'stock': producto.stock
        }), 200
    except Exception as e:
        return jsonify({'mensaje': 'Producto no encontrado'}), 404

@app.route('/api/productos', methods=['POST'])
def crear_producto():
    try:
        data = request.get_json()
        
        nuevo_producto = Producto(
            nombre=data['nombre'],
            descripcion=data.get('descripcion', ''),
            precio=data['precio'],
            talla=data.get('talla', ''),
            color=data.get('color', ''),
            imagen_url=data.get('imagen_url', ''),
            stock=data.get('stock', 0)
        )
        
        db.session.add(nuevo_producto)
        db.session.commit()
        
        return jsonify({'mensaje': 'Producto creado exitosamente', 'id': nuevo_producto.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'mensaje': f'Error al crear producto: {str(e)}'}), 500

# Rutas del Carrito
@app.route('/api/carrito', methods=['GET'])
@token_requerido
def obtener_carrito(usuario_actual):
    try:
        items = Carrito.query.filter_by(usuario_id=usuario_actual.id).all()
        
        resultado = []
        total = 0
        
        for item in items:
            subtotal = item.producto.precio * item.cantidad
            total += subtotal
            
            resultado.append({
                'id': item.id,
                'producto': {
                    'id': item.producto.id,
                    'nombre': item.producto.nombre,
                    'precio': item.producto.precio,
                    'imagen_url': item.producto.imagen_url
                },
                'cantidad': item.cantidad,
                'subtotal': subtotal
            })
        
        return jsonify({
            'items': resultado,
            'total': total
        }), 200
    except Exception as e:
        return jsonify({'mensaje': f'Error al obtener carrito: {str(e)}'}), 500

@app.route('/api/carrito', methods=['POST'])
@token_requerido
def agregar_al_carrito(usuario_actual):
    try:
        data = request.get_json()
        
        if not data or not data.get('producto_id'):
            return jsonify({'mensaje': 'ID de producto requerido'}), 400
        
        producto = Producto.query.get(data['producto_id'])
        if not producto:
            return jsonify({'mensaje': 'Producto no encontrado'}), 404
        
        # Verificar si el producto ya está en el carrito
        item_existente = Carrito.query.filter_by(
            usuario_id=usuario_actual.id,
            producto_id=data['producto_id']
        ).first()
        
        if item_existente:
            item_existente.cantidad += data.get('cantidad', 1)
            db.session.commit()
            return jsonify({'mensaje': 'Cantidad actualizada en el carrito'}), 200
        
        nuevo_item = Carrito(
            usuario_id=usuario_actual.id,
            producto_id=data['producto_id'],
            cantidad=data.get('cantidad', 1)
        )
        
        db.session.add(nuevo_item)
        db.session.commit()
        
        return jsonify({'mensaje': 'Item añadido exitosamente al carrito'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'mensaje': f'Error al agregar al carrito: {str(e)}'}), 500

@app.route('/api/carrito/<int:id>', methods=['DELETE'])
@token_requerido
def eliminar_del_carrito(usuario_actual, id):
    try:
        item = Carrito.query.filter_by(id=id, usuario_id=usuario_actual.id).first()
        
        if not item:
            return jsonify({'mensaje': 'Item no encontrado en el carrito'}), 404
        
        db.session.delete(item)
        db.session.commit()
        
        return jsonify({'mensaje': 'Item eliminado del carrito'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'mensaje': f'Error al eliminar del carrito: {str(e)}'}), 500

@app.route('/api/carrito/<int:id>', methods=['PUT'])
@token_requerido
def actualizar_cantidad_carrito(usuario_actual, id):
    try:
        data = request.get_json()
        item = Carrito.query.filter_by(id=id, usuario_id=usuario_actual.id).first()
        
        if not item:
            return jsonify({'mensaje': 'Item no encontrado'}), 404
        
        cantidad = data.get('cantidad', 1)
        
        if cantidad <= 0:
            db.session.delete(item)
        else:
            item.cantidad = cantidad
        
        db.session.commit()
        
        return jsonify({'mensaje': 'Cantidad actualizada'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'mensaje': f'Error al actualizar cantidad: {str(e)}'}), 500

@app.route('/api/carrito/vaciar', methods=['DELETE'])
@token_requerido
def vaciar_carrito(usuario_actual):
    try:
        Carrito.query.filter_by(usuario_id=usuario_actual.id).delete()
        db.session.commit()
        
        return jsonify({'mensaje': 'Carrito vaciado exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'mensaje': f'Error al vaciar carrito: {str(e)}'}), 500

# ==================== CATEGORÍAS ====================

@app.route('/api/categorias', methods=['GET'])
def obtener_categorias():
    try:
        categorias = Categoria.query.all()
        resultado = []
        for c in categorias:
            resultado.append({
                'id': c.id,
                'nombre': c.nombre,
                'descripcion': c.descripcion,
                'num_productos': len(c.productos)
            })
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'mensaje': f'Error al obtener categorías: {str(e)}'}), 500

@app.route('/api/categorias', methods=['POST'])
@admin_requerido
def crear_categoria(usuario_actual):
    try:
        data = request.get_json()
        if not data or not data.get('nombre'):
            return jsonify({'mensaje': 'Nombre de categoría requerido'}), 400
        
        nueva_categoria = Categoria(
            nombre=data['nombre'],
            descripcion=data.get('descripcion', '')
        )
        db.session.add(nueva_categoria)
        db.session.commit()
        
        return jsonify({
            'mensaje': 'Categoría creada exitosamente',
            'id': nueva_categoria.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'mensaje': f'Error al crear categoría: {str(e)}'}), 500

# ==================== PEDIDOS ====================

@app.route('/api/pedidos', methods=['POST'])
@token_requerido
def crear_pedido(usuario_actual):
    try:
        data = request.get_json()
        
        # Obtener items del carrito
        items_carrito = Carrito.query.filter_by(usuario_id=usuario_actual.id).all()
        
        if not items_carrito:
            return jsonify({'mensaje': 'El carrito está vacío'}), 400
        
        # Calcular total
        total = 0
        items_pedido = []
        
        for item in items_carrito:
            if item.producto.stock < item.cantidad:
                return jsonify({
                    'mensaje': f'Stock insuficiente para {item.producto.nombre}'
                }), 400
            
            subtotal = item.producto.precio * item.cantidad
            total += subtotal
            
            items_pedido.append({
                'producto_id': item.producto.id,
                'cantidad': item.cantidad,
                'precio_unitario': item.producto.precio
            })
        
        # Crear pedido
        nuevo_pedido = Pedido(
            usuario_id=usuario_actual.id,
            total=total,
            estado='pendiente',
            direccion_envio=data.get('direccion_envio', '')
        )
        db.session.add(nuevo_pedido)
        db.session.flush()
        
        # Crear items del pedido
        for item_data in items_pedido:
            item_pedido = ItemPedido(
                pedido_id=nuevo_pedido.id,
                producto_id=item_data['producto_id'],
                cantidad=item_data['cantidad'],
                precio_unitario=item_data['precio_unitario']
            )
            db.session.add(item_pedido)
        
        db.session.commit()
        
        return jsonify({
            'mensaje': 'Pedido creado exitosamente',
            'pedido_id': nuevo_pedido.id,
            'total': total
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'mensaje': f'Error al crear pedido: {str(e)}'}), 500

@app.route('/api/pedidos', methods=['GET'])
@token_requerido
def obtener_pedidos_usuario(usuario_actual):
    try:
        pedidos = Pedido.query.filter_by(usuario_id=usuario_actual.id).order_by(Pedido.fecha_pedido.desc()).all()
        
        resultado = []
        for pedido in pedidos:
            items = []
            for item in pedido.items:
                items.append({
                    'producto': {
                        'id': item.producto.id,
                        'nombre': item.producto.nombre,
                        'imagen_url': item.producto.imagen_url
                    },
                    'cantidad': item.cantidad,
                    'precio_unitario': item.precio_unitario,
                    'subtotal': item.cantidad * item.precio_unitario
                })
            
            resultado.append({
                'id': pedido.id,
                'fecha': pedido.fecha_pedido.strftime('%Y-%m-%d %H:%M:%S'),
                'total': pedido.total,
                'estado': pedido.estado,
                'items': items
            })
        
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'mensaje': f'Error al obtener pedidos: {str(e)}'}), 500

# ==================== STRIPE PAGOS ====================

@app.route('/api/stripe/config', methods=['GET'])
def get_stripe_config():
    return jsonify({
        'publicKey': os.environ.get('STRIPE_PUBLIC_KEY', 'pk_test_tu_clave_publica_aqui')
    })

@app.route('/api/stripe/create-payment-intent', methods=['POST'])
@token_requerido
def create_payment_intent(usuario_actual):
    try:
        data = request.get_json()
        pedido_id = data.get('pedido_id')
        
        if not pedido_id:
            return jsonify({'mensaje': 'ID de pedido requerido'}), 400
        
        pedido = Pedido.query.get(pedido_id)
        
        if not pedido or pedido.usuario_id != usuario_actual.id:
            return jsonify({'mensaje': 'Pedido no encontrado'}), 404
        
        # Crear Payment Intent con Stripe
        intent = stripe.PaymentIntent.create(
            amount=int(pedido.total),  # Stripe usa centavos, pero COP no tiene centavos
            currency='cop',
            metadata={
                'pedido_id': pedido.id,
                'usuario_id': usuario_actual.id
            }
        )
        
        return jsonify({
            'clientSecret': intent.client_secret,
            'pedido_id': pedido.id
        }), 200
        
    except Exception as e:
        return jsonify({'mensaje': f'Error al crear payment intent: {str(e)}'}), 500

@app.route('/api/stripe/webhook', methods=['POST'])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, 'whsec_your_webhook_secret'  # Cambia esto por tu webhook secret
        )
    except ValueError as e:
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        return jsonify({'error': 'Invalid signature'}), 400
    
    # Manejar el evento
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        pedido_id = payment_intent['metadata']['pedido_id']
        
        # Actualizar pedido
        pedido = Pedido.query.get(pedido_id)
        if pedido:
            pedido.estado = 'pagado'
            pedido.stripe_payment_id = payment_intent['id']
            
            # Reducir stock de productos
            for item in pedido.items:
                producto = Producto.query.get(item.producto_id)
                if producto:
                    producto.stock -= item.cantidad
            
            # Vaciar carrito del usuario
            Carrito.query.filter_by(usuario_id=pedido.usuario_id).delete()
            
            db.session.commit()
    
    return jsonify({'status': 'success'}), 200

@app.route('/api/pedidos/<int:pedido_id>/confirmar-pago', methods=['POST'])
@token_requerido
def confirmar_pago(usuario_actual, pedido_id):
    try:
        data = request.get_json()
        payment_intent_id = data.get('payment_intent_id')
        
        pedido = Pedido.query.get(pedido_id)
        
        if not pedido or pedido.usuario_id != usuario_actual.id:
            return jsonify({'mensaje': 'Pedido no encontrado'}), 404
        
        # Actualizar estado del pedido
        pedido.estado = 'pagado'
        pedido.stripe_payment_id = payment_intent_id
        
        # Reducir stock de productos
        for item in pedido.items:
            producto = Producto.query.get(item.producto_id)
            if producto:
                producto.stock -= item.cantidad
        
        # Vaciar carrito
        Carrito.query.filter_by(usuario_id=usuario_actual.id).delete()
        
        db.session.commit()
        
        return jsonify({'mensaje': 'Pago confirmado exitosamente'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'mensaje': f'Error al confirmar pago: {str(e)}'}), 500

# ==================== ADMINISTRACIÓN ====================

@app.route('/api/admin/pedidos', methods=['GET'])
@admin_requerido
def obtener_todos_pedidos(usuario_actual):
    try:
        estado = request.args.get('estado')
        
        if estado:
            pedidos = Pedido.query.filter_by(estado=estado).order_by(Pedido.fecha_pedido.desc()).all()
        else:
            pedidos = Pedido.query.order_by(Pedido.fecha_pedido.desc()).all()
        
        resultado = []
        for pedido in pedidos:
            items = []
            for item in pedido.items:
                items.append({
                    'producto': {
                        'id': item.producto.id,
                        'nombre': item.producto.nombre,
                        'imagen_url': item.producto.imagen_url
                    },
                    'cantidad': item.cantidad,
                    'precio_unitario': item.precio_unitario,
                    'subtotal': item.cantidad * item.precio_unitario
                })
            
            resultado.append({
                'id': pedido.id,
                'usuario': {
                    'id': pedido.usuario.id,
                    'nombre': pedido.usuario.nombre,
                    'email': pedido.usuario.email
                },
                'fecha': pedido.fecha_pedido.strftime('%Y-%m-%d %H:%M:%S'),
                'total': pedido.total,
                'estado': pedido.estado,
                'direccion_envio': pedido.direccion_envio,
                'items': items
            })
        
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'mensaje': f'Error al obtener pedidos: {str(e)}'}), 500

@app.route('/api/admin/pedidos/<int:pedido_id>/estado', methods=['PUT'])
@admin_requerido
def actualizar_estado_pedido(usuario_actual, pedido_id):
    try:
        data = request.get_json()
        nuevo_estado = data.get('estado')
        
        if not nuevo_estado:
            return jsonify({'mensaje': 'Estado requerido'}), 400
        
        estados_validos = ['pendiente', 'pagado', 'despachado', 'completado', 'cancelado']
        if nuevo_estado not in estados_validos:
            return jsonify({'mensaje': 'Estado inválido'}), 400
        
        pedido = Pedido.query.get(pedido_id)
        if not pedido:
            return jsonify({'mensaje': 'Pedido no encontrado'}), 404
        
        pedido.estado = nuevo_estado
        db.session.commit()
        
        return jsonify({'mensaje': 'Estado actualizado exitosamente'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'mensaje': f'Error al actualizar estado: {str(e)}'}), 500

@app.route('/api/admin/productos/<int:producto_id>', methods=['PUT'])
@admin_requerido
def actualizar_producto(usuario_actual, producto_id):
    try:
        data = request.get_json()
        producto = Producto.query.get(producto_id)
        
        if not producto:
            return jsonify({'mensaje': 'Producto no encontrado'}), 404
        
        # Actualizar campos
        if 'nombre' in data:
            producto.nombre = data['nombre']
        if 'descripcion' in data:
            producto.descripcion = data['descripcion']
        if 'precio' in data:
            producto.precio = data['precio']
        if 'stock' in data:
            producto.stock = data['stock']
        if 'talla' in data:
            producto.talla = data['talla']
        if 'color' in data:
            producto.color = data['color']
        if 'categoria_id' in data:
            producto.categoria_id = data['categoria_id']
        if 'imagen_url' in data:
            producto.imagen_url = data['imagen_url']
        
        db.session.commit()
        
        return jsonify({'mensaje': 'Producto actualizado exitosamente'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'mensaje': f'Error al actualizar producto: {str(e)}'}), 500

@app.route('/api/admin/productos/<int:producto_id>', methods=['DELETE'])
@admin_requerido
def eliminar_producto(usuario_actual, producto_id):
    try:
        producto = Producto.query.get(producto_id)
        
        if not producto:
            return jsonify({'mensaje': 'Producto no encontrado'}), 404
        
        db.session.delete(producto)
        db.session.commit()
        
        return jsonify({'mensaje': 'Producto eliminado exitosamente'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'mensaje': f'Error al eliminar producto: {str(e)}'}), 500

@app.route('/api/admin/productos', methods=['POST'])
@admin_requerido
def crear_producto_admin(usuario_actual):
    try:
        data = request.get_json()
        
        if not data or not data.get('nombre') or not data.get('precio'):
            return jsonify({'mensaje': 'Nombre y precio son requeridos'}), 400
        
        nuevo_producto = Producto(
            nombre=data['nombre'],
            descripcion=data.get('descripcion', ''),
            precio=data['precio'],
            talla=data.get('talla', ''),
            color=data.get('color', ''),
            imagen_url=data.get('imagen_url', ''),
            stock=data.get('stock', 0),
            categoria_id=data.get('categoria_id')
        )
        
        db.session.add(nuevo_producto)
        db.session.commit()
        
        return jsonify({
            'mensaje': 'Producto creado exitosamente',
            'id': nuevo_producto.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'mensaje': f'Error al crear producto: {str(e)}'}), 500

@app.route('/api/admin/upload-imagen', methods=['POST'])
@admin_requerido
def upload_imagen(usuario_actual):
    try:
        if 'imagen' not in request.files:
            return jsonify({'mensaje': 'No se encontró archivo'}), 400
        
        file = request.files['imagen']
        
        if file.filename == '':
            return jsonify({'mensaje': 'No se seleccionó archivo'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Agregar timestamp para evitar colisiones
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_')
            filename = timestamp + filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            return jsonify({
                'mensaje': 'Imagen subida exitosamente',
                'imagen_url': f'imagenes/{filename}'
            }), 200
        else:
            return jsonify({'mensaje': 'Tipo de archivo no permitido'}), 400
            
    except Exception as e:
        return jsonify({'mensaje': f'Error al subir imagen: {str(e)}'}), 500

@app.route('/api/admin/estadisticas', methods=['GET'])
@admin_requerido
def obtener_estadisticas(usuario_actual):
    try:
        total_pedidos = Pedido.query.count()
        pedidos_pendientes = Pedido.query.filter_by(estado='pendiente').count()
        pedidos_pagados = Pedido.query.filter_by(estado='pagado').count()
        pedidos_despachados = Pedido.query.filter_by(estado='despachado').count()
        
        total_ventas = db.session.query(db.func.sum(Pedido.total)).filter(
            Pedido.estado.in_(['pagado', 'despachado', 'completado'])
        ).scalar() or 0
        
        total_productos = Producto.query.count()
        productos_sin_stock = Producto.query.filter_by(stock=0).count()
        
        return jsonify({
            'pedidos': {
                'total': total_pedidos,
                'pendientes': pedidos_pendientes,
                'pagados': pedidos_pagados,
                'despachados': pedidos_despachados
            },
            'ventas': {
                'total': total_ventas
            },
            'productos': {
                'total': total_productos,
                'sin_stock': productos_sin_stock
            }
        }), 200
        
    except Exception as e:
        return jsonify({'mensaje': f'Error al obtener estadísticas: {str(e)}'}), 500

# Ruta de salud del servidor
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'mensaje': 'Servidor funcionando correctamente'}), 200

# Inicializar base de datos
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    print("🚀 Servidor iniciado en http://localhost:5000")
    print("📦 Base de datos: tienda_vestidos.db")
    print("✨ GLAM RENT - Backend activo")
    app.run(debug=True, port=5000)