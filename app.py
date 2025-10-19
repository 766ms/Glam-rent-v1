from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'glam-rent-cartagena-2024-super-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tienda_vestidos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app)
db = SQLAlchemy(app)

# Modelos de Base de Datos
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    carritos = db.relationship('Carrito', backref='usuario', lazy=True, cascade='all, delete-orphan')

class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    precio = db.Column(db.Float, nullable=False)
    talla = db.Column(db.String(10))
    color = db.Column(db.String(50))
    imagen_url = db.Column(db.String(300))
    stock = db.Column(db.Integer, default=0)

class Carrito(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    cantidad = db.Column(db.Integer, default=1)
    fecha_agregado = db.Column(db.DateTime, default=datetime.datetime.utcnow)
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
                'email': usuario.email
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