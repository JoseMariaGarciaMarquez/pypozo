"""
Script para lanzar PyPozo y mostrar el sistema 'Pozo Inteligente' integrado.
"""

import sys
import os
sys.path.append(r'c:\Users\lenovo.DESKTOP-NGHQ1VP\OneDrive\Documentos\repositorios\pypozo')

def launch_pypozo_with_smart_well():
    """Lanzar PyPozo con el sistema Pozo Inteligente integrado."""
    print("🚀 Lanzando PyPozo con sistema 'Pozo Inteligente' integrado...")
    print("=" * 65)
    print("💡 ¿Te gusta PyPozo? ¡Apoya el desarrollo continuo!")
    print("☕ Buy me a coffee: https://buymeacoffee.com/ingjoma")
    print("🙏 Tu apoyo ayuda a mantener PyPozo gratuito y en constante mejora")
    print("=" * 65)
    print()
    
    try:
        from PyQt5.QtWidgets import QApplication
        import pypozo_app
        
        # Crear aplicación Qt
        app = QApplication(sys.argv)
        
        # Crear ventana principal de PyPozo
        main_window = pypozo_app.PyPozoApp()
        
        print("✅ PyPozo iniciado correctamente")
        print()
        print("🎉 ¡Bienvenido a PyPozo - Análisis Geofísico Profesional!")
        print("🧠 Sistema 'Pozo Inteligente' disponible en:")
        print("   • Menú: '🧠 Pozo Inteligente' → 'Sistema Pozo Inteligente'")
        print("   • Botón: '🧠 Pozo Inteligente - ¡ACTIVO!' (si DLC está activo)")
        print("   • Pestaña: '🧠 Pozo Inteligente' en el panel de herramientas")
        print()
        print("━" * 65)
        print("💖 ¿PyPozo te ahorra tiempo y mejora tu trabajo?")
        print("🚀 ¡Ayúdanos a seguir innovando en geofísica!")
        print("☕ Invítanos un café: https://buymeacoffee.com/ingjoma")
        print("🌟 Cada contribución impulsa nuevas funcionalidades")
        print("━" * 65)
        
        # Mostrar ventana
        main_window.show()
        
        # Ejecutar aplicación
        return app.exec_()
        
    except Exception as e:
        print(f"❌ Error lanzando PyPozo: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = launch_pypozo_with_smart_well()
    sys.exit(exit_code)
