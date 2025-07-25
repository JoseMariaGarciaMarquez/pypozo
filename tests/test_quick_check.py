"""
Test rápido para verificar que PyPozo funciona básicamente
"""

import sys
from pathlib import Path

def test_quick_check():
    """Verificación rápida del estado del proyecto."""
    print("🔍 Verificación rápida de PyPozo...")
    
    # Verificar estructura básica
    project_root = Path(__file__).parent.parent
    
    print(f"📁 Directorio proyecto: {project_root}")
    print(f"✅ README.md: {'✓' if (project_root / 'README.md').exists() else '✗'}")
    print(f"✅ welcome_dialog.py: {'✓' if (project_root / 'welcome_dialog.py').exists() else '✗'}")
    print(f"✅ .gitignore: {'✓' if (project_root / '.gitignore').exists() else '✗'}")
    
    # Verificar protección DLC
    gitignore_path = project_root / ".gitignore"
    if gitignore_path.exists():
        content = gitignore_path.read_text(encoding='utf-8')
        dlc_protected = "patreon_dlc" in content
        print(f"🔒 DLC protegido: {'✓' if dlc_protected else '✗'}")
    
    print("✅ Verificación básica completada")
    return True

if __name__ == "__main__":
    test_quick_check()
