from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tienda_vestidos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

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

class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    descripcion = db.Column(db.Text)

def seed_products():
    with app.app_context():
        # Crear tablas
        db.create_all()
        
        # Verificar si ya hay productos
        if Producto.query.count() > 0:
            print("⚠️  Ya existen productos en la base de datos.")
            respuesta = input("¿Deseas eliminarlos y crear nuevos? (s/n): ")
            if respuesta.lower() == 's':
                Producto.query.delete()
                db.session.commit()
                print("🗑️  Productos anteriores eliminados.")
            else:
                print("❌ Operación cancelada.")
                return
        
        # Crear categorías si no existen
        print("\n📦 Verificando categorías...")
        categorias_data = {
            'Vestidos de Gala': {
                'descripcion': 'Elegantes vestidos para eventos especiales y ocasiones formales'
            },
            'Corsés': {
                'descripcion': 'Corsés de diseño exclusivo con ajuste perfecto'
            },
            'Vestidos Corset': {
                'descripcion': 'Vestidos con detalles de corsé, combinación perfecta de elegancia y estilo'
            }
        }
        
        categorias = {}
        for nombre, data in categorias_data.items():
            categoria = Categoria.query.filter_by(nombre=nombre).first()
            if not categoria:
                categoria = Categoria(nombre=nombre, descripcion=data['descripcion'])
                db.session.add(categoria)
                db.session.flush()
                print(f"   ✅ Categoría creada: {nombre}")
            else:
                print(f"   ℹ️  Categoría existente: {nombre}")
            categorias[nombre] = categoria.id
        
        db.session.commit()
        
        # Productos destacados y corsés con precios y categorías
        productos = [
            # VESTIDOS DESTACADOS
            {
                'nombre': 'Wings of Losie Corset Dress',
                'descripcion': 'Elegante vestido con corsé estilo wings, perfecto para eventos especiales',
                'precio': 299999,
                'talla': 'S/M/L',
                'color': 'Rosa',
                'imagen_url': 'imagenes/vestido 1.png',
                'stock': 10,
                'categoria_id': categorias['Vestidos de Gala']
            },
            {
                'nombre': 'Secret Envoy Dress',
                'descripcion': 'Vestido secreto de gala con detalles únicos',
                'precio': 199999,
                'talla': 'S/M/L',
                'color': 'Blanco',
                'imagen_url': 'imagenes/vestido 2.png',
                'stock': 15,
                'categoria_id': categorias['Vestidos de Gala']
            },
            {
                'nombre': 'Flowing Light Hymn Dress',
                'descripcion': 'Vestido fluido con detalles de luz, diseño exclusivo',
                'precio': 399999,
                'talla': 'S/M/L',
                'color': 'Azul',
                'imagen_url': 'imagenes/vestido 3.png',
                'stock': 8,
                'categoria_id': categorias['Vestidos de Gala']
            },
            # CORSÉS CON PRECIOS
            {
                'nombre': 'Perla Encantada',
                'descripcion': 'Corsé elegante con detalles de perlas incrustadas',
                'precio': 249999,
                'talla': 'S/M/L',
                'color': 'Perla',
                'imagen_url': 'imagenes/CORSET 3.png',
                'stock': 12,
                'categoria_id': categorias['Corsés']
            },
            {
                'nombre': 'Dama Carmesí',
                'descripcion': 'Corsé rojo carmesí con ajuste perfecto',
                'precio': 189999,
                'talla': 'S/M/L',
                'color': 'Rojo',
                'imagen_url': 'imagenes/CORSET 4.png',
                'stock': 10,
                'categoria_id': categorias['Corsés']
            },
            {
                'nombre': 'Aurora de Cristal',
                'descripcion': 'Corsé con cristales brillantes, diseño premium',
                'precio': 329999,
                'talla': 'S/M/L',
                'color': 'Cristal',
                'imagen_url': 'imagenes/CORSET 5.png',
                'stock': 7,
                'categoria_id': categorias['Corsés']
            },
            {
                'nombre': 'Susurro de Cielo',
                'descripcion': 'Corsé celestial azul con bordados delicados',
                'precio': 159999,
                'talla': 'S/M/L',
                'color': 'Azul Cielo',
                'imagen_url': 'imagenes/CORSET 6.png',
                'stock': 9,
                'categoria_id': categorias['Corsés']
            },
            {
                'nombre': 'Rosa de Ensueño',
                'descripcion': 'Corsé rosa de ensueño con detalles románticos',
                'precio': 219999,
                'talla': 'S/M/L',
                'color': 'Rosa',
                'imagen_url': 'imagenes/CORSET 7.png',
                'stock': 11,
                'categoria_id': categorias['Corsés']
            },
            {
                'nombre': 'Jardín Secreto',
                'descripcion': 'Vestido corsé con detalles florales y encajes',
                'precio': 349999,
                'talla': 'S/M/L',
                'color': 'Verde',
                'imagen_url': 'imagenes/VESTIDO CORSET 1.png',
                'stock': 6,
                'categoria_id': categorias['Vestidos Corset']
            }
        ]
        
        # Insertar productos
        print("\n📦 Insertando productos...")
        for producto_data in productos:
            producto = Producto(**producto_data)
            db.session.add(producto)
        
        db.session.commit()
        print(f"✅ {len(productos)} productos insertados exitosamente!")
        
        # Mostrar productos insertados
        print("\n" + "="*70)
        print("📋 PRODUCTOS EN LA BASE DE DATOS:")
        print("="*70)
        for p in Producto.query.all():
            cat = Categoria.query.get(p.categoria_id)
            cat_nombre = cat.nombre if cat else 'Sin categoría'
            print(f"ID: {p.id:2d} | {p.nombre:35s} | {cat_nombre:20s} | ${p.precio:>10,.0f} COP | Stock: {p.stock}")
        print("="*70)
        print("\n🎉 ¡Base de datos lista para usar!")

if __name__ == '__main__':
    print("🌟 GLAM RENT - Inicializador de Base de Datos")
    print("=" * 70)
    seed_products()