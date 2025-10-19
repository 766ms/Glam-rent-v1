from app import app, db, Usuario, Categoria, Producto
from werkzeug.security import generate_password_hash

with app.app_context():
    # Crear todas las tablas
    db.create_all()
    
    # Crear admin
    admin = Usuario(
        nombre='Admin',
        email='admin@glamrent.com',
        password=generate_password_hash('admin123'),
        es_admin=True
    )
    db.session.add(admin)
    
    # Crear categorías
    cat1 = Categoria(nombre='Vestidos de Gala', descripcion='Vestidos elegantes')
    cat2 = Categoria(nombre='Corsés', descripcion='Corsés de diseño')
    db.session.add(cat1)
    db.session.add(cat2)
    db.session.commit()
    
    print('✅ TODO CREADO!')
    print('Email: admin@glamrent.com')
    print('Pass: admin123')
