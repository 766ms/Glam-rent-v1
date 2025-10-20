from app import app, db, Usuario, Categoria
from werkzeug.security import generate_password_hash

def inicializar_base_datos():
    """Inicializa la base de datos con admin y categorías"""
    
    with app.app_context():
        # Crear todas las tablas
        db.create_all()
        print("✅ Tablas creadas")
        
        # Verificar si ya existe el admin
        admin_existe = Usuario.query.filter_by(email='admin@glamrent.com').first()
        
        if not admin_existe:
            # Crear usuario admin
            admin = Usuario(
                nombre='Admin',
                email='admin@glamrent.com',
                password=generate_password_hash('admin123'),
                es_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Usuario admin creado: admin@glamrent.com / admin123")
        else:
            print("ℹ️  Usuario admin ya existe")
        
        # Crear categorías básicas si no existen
        categorias_base = [
            'Vestidos de Fiesta',
            'Vestidos de Noche',
            'Vestidos Casuales',
            'Vestidos de Graduación',
            'Vestidos de Coctel'
        ]
        
        for nombre_cat in categorias_base:
            cat_existe = Categoria.query.filter_by(nombre=nombre_cat).first()
            if not cat_existe:
                nueva_cat = Categoria(nombre=nombre_cat)
                db.session.add(nueva_cat)
        
        db.session.commit()
        print("✅ Categorías creadas")
        
        print("\n" + "="*50)
        print("🎉 BASE DE DATOS INICIALIZADA CORRECTAMENTE")
        print("="*50)
        print("\n📋 CREDENCIALES DE ADMIN:")
        print("   Email: admin@glamrent.com")
        print("   Password: admin123")
        print("\n🚀 Ahora ejecuta: python app.py")
        print("="*50 + "\n")

if __name__ == '__main__':
    inicializar_base_datos()