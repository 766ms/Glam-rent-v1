from app import app, db, Usuario, Categoria
from werkzeug.security import generate_password_hash

def crear_admin():
    """Crea el usuario admin y categorías básicas"""
    
    with app.app_context():
        # Crear tablas si no existen
        db.create_all()
        print("✅ Tablas verificadas")
        
        # Verificar si ya existe el admin
        admin_existe = Usuario.query.filter_by(email='admin@glamrent.com').first()
        
        if admin_existe:
            # Si existe, actualizar para asegurar que es admin
            admin_existe.es_admin = True
            admin_existe.password = generate_password_hash('admin123')
            db.session.commit()
            print("✅ Usuario admin actualizado: admin@glamrent.com / admin123")
        else:
            # Crear nuevo usuario admin
            admin = Usuario(
                nombre='Admin',
                email='admin@glamrent.com',
                password=generate_password_hash('admin123'),
                es_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Usuario admin creado: admin@glamrent.com / admin123")
        
        # Crear categorías básicas si no existen
        categorias_base = [
            'Vestidos de Fiesta',
            'Vestidos de Noche',
            'Vestidos Casuales',
            'Vestidos de Graduación',
            'Vestidos de Coctel'
        ]
        
        categorias_creadas = 0
        for nombre_cat in categorias_base:
            cat_existe = Categoria.query.filter_by(nombre=nombre_cat).first()
            if not cat_existe:
                nueva_cat = Categoria(nombre=nombre_cat)
                db.session.add(nueva_cat)
                categorias_creadas += 1
        
        if categorias_creadas > 0:
            db.session.commit()
            print(f"✅ {categorias_creadas} categorías creadas")
        else:
            print("ℹ️  Todas las categorías ya existen")
        
        print("\n" + "="*60)
        print("✅ ADMIN CREADO EXITOSAMENTE")
        print("="*60)
        print("\n📋 CREDENCIALES:")
        print("   Email: admin@glamrent.com")
        print("   Password: admin123")
        print("\n🚀 Ahora ejecuta: python app.py")
        print("="*60 + "\n")

if __name__ == '__main__':
    crear_admin()