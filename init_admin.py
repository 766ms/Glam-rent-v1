from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tienda_vestidos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Importar modelos (necesitamos definirlos aquí porque no podemos importar app.py directamente)
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    es_admin = db.Column(db.Boolean, default=False)

class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    descripcion = db.Column(db.Text)

def init_admin_and_categories():
    with app.app_context():
        print("🔧 Inicializando Administrador y Categorías...")
        print("="*70)
        
        # Crear todas las tablas
        db.create_all()
        print("✅ Tablas de la base de datos creadas/verificadas")
        print()
        
        # Crear usuario administrador
        admin_email = "admin@glamrent.com"
        admin_exists = Usuario.query.filter_by(email=admin_email).first()
        
        if not admin_exists:
            admin_password = "admin123"  # Cambia esto por una contraseña segura
            admin = Usuario(
                nombre="Administrador",
                email=admin_email,
                password=generate_password_hash(admin_password),
                es_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print(f"✅ Usuario administrador creado:")
            print(f"   Email: {admin_email}")
            print(f"   Contraseña: {admin_password}")
            print(f"   ⚠️  IMPORTANTE: Cambia esta contraseña después del primer login")
        else:
            print(f"ℹ️  Usuario administrador ya existe: {admin_email}")
            # Actualizar para asegurarse de que es admin
            admin_exists.es_admin = True
            db.session.commit()
            print(f"   Actualizado para tener permisos de admin")
        
        print()
        print("-"*70)
        
        # Crear categorías predeterminadas
        categorias_default = [
            {
                'nombre': 'Vestidos de Gala',
                'descripcion': 'Elegantes vestidos para eventos especiales y ocasiones formales'
            },
            {
                'nombre': 'Corsés',
                'descripcion': 'Corsés de diseño exclusivo con ajuste perfecto'
            },
            {
                'nombre': 'Vestidos Corset',
                'descripcion': 'Vestidos con detalles de corsé, combinación perfecta de elegancia y estilo'
            },
            {
                'nombre': 'Colección de Verano',
                'descripcion': 'Piezas frescas y coloridas para la temporada de verano'
            }
        ]
        
        print("\n📦 Creando categorías...")
        categorias_creadas = 0
        
        for cat_data in categorias_default:
            categoria_existe = Categoria.query.filter_by(nombre=cat_data['nombre']).first()
            if not categoria_existe:
                categoria = Categoria(**cat_data)
                db.session.add(categoria)
                categorias_creadas += 1
                print(f"   ✅ Categoría creada: {cat_data['nombre']}")
            else:
                print(f"   ℹ️  Categoría ya existe: {cat_data['nombre']}")
        
        db.session.commit()
        
        print()
        print("="*70)
        print(f"\n✨ Inicialización completada!")
        print(f"   • Categorías creadas: {categorias_creadas}")
        print(f"   • Total de categorías: {Categoria.query.count()}")
        print()
        print("🚀 Puedes iniciar sesión en el panel de administración con:")
        print(f"   Email: {admin_email}")
        if not admin_exists:
            print(f"   Contraseña: admin123")
        print()
        print("🌐 Para acceder al panel de admin, ve a: http://localhost:5000/admin.html")
        print("="*70)

if __name__ == '__main__':
    init_admin_and_categories()
