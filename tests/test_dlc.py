#!/usr/bin/env python3
"""
Test de detección del DLC Patreon para PyPozo
"""

import sys
from pathlib import Path

def test_dlc_detection():
    """Probar detección del DLC."""
    print("🔍 Probando detección del DLC Patreon...")
    
    # Función de detección (copia de pypozo_app.py)
    def check_patreon_dlc():
        dlc_path = Path(__file__).parent / "patreon_dlc"
        return dlc_path.exists() and (dlc_path / "__init__.py").exists()

    def load_patreon_features():
        if check_patreon_dlc():
            try:
                sys.path.insert(0, str(Path(__file__).parent / "patreon_dlc"))
                import neural_completion
                return neural_completion
            except ImportError as e:
                print(f"❌ Error importando DLC: {e}")
                return None
        return None
    
    # Probar detección
    has_dlc = check_patreon_dlc()
    print(f"📁 Carpeta DLC detectada: {'✅ SÍ' if has_dlc else '❌ NO'}")
    
    if has_dlc:
        dlc_path = Path(__file__).parent / "patreon_dlc"
        files = list(dlc_path.glob("*.py"))
        print(f"📋 Archivos Python encontrados: {[f.name for f in files]}")
        
        # Probar carga
        dlc = load_patreon_features()
        if dlc:
            print("✅ DLC cargado exitosamente!")
            print(f"📦 Funciones disponibles:")
            functions = [attr for attr in dir(dlc) if not attr.startswith('_')]
            for func in functions:
                print(f"   • {func}")
            
            # Probar función específica
            try:
                dialog_func = getattr(dlc, 'create_completion_dialog', None)
                if dialog_func:
                    print("🎯 Función de diálogo encontrada!")
                else:
                    print("⚠️ Función de diálogo no encontrada")
            except Exception as e:
                print(f"⚠️ Error probando función: {e}")
        else:
            print("❌ Error cargando DLC")
    else:
        print("💡 Para habilitar funciones premium:")
        print("   1. Suscríbete a Patreon nivel 3 ($15/mes)")
        print("   2. Descarga el DLC desde tu página de Patreon")
        print("   3. Extrae la carpeta 'patreon_dlc' en esta ubicación")

if __name__ == "__main__":
    test_dlc_detection()
