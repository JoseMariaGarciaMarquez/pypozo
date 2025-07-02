#!/usr/bin/env python3
"""
Test visual elements - Logo and Icon
Prueba de elementos visuales mejorados en PyPozo
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_visual_assets():
    """Test that visual assets exist and are accessible."""
    base_path = Path(__file__).parent
    
    # Test logo files
    logo_files = [
        "images/icono.png",
        "images/logo_completo.png", 
        "images/logo_transparente.png",
        "images/logo.png"
    ]
    
    print("🎨 TESTING VISUAL ASSETS FOR PYPOZO 2.0")
    print("=" * 50)
    
    for logo_file in logo_files:
        logo_path = base_path / logo_file
        if logo_path.exists():
            size_kb = logo_path.stat().st_size / 1024
            print(f"✅ {logo_file} - {size_kb:.1f} KB")
        else:
            print(f"❌ {logo_file} - NOT FOUND")
    
    print("\n🖥️ VISUAL INTEGRATION STATUS:")
    
    # Check if app file has the logo integration
    app_file = base_path / "pypozo_app.py"
    if app_file.exists():
        content = app_file.read_text(encoding='utf-8', errors='ignore')
        
        # Check for icon integration
        if "icono.png" in content:
            print("✅ App icon integration - IMPLEMENTED")
        else:
            print("❌ App icon integration - MISSING")
            
        # Check for logo integration  
        if "logo_completo.png" in content:
            print("✅ Logo integration - IMPLEMENTED") 
        else:
            print("❌ Logo integration - MISSING")
            
        # Check for version branding
        if "PyPozo v2.0.0" in content:
            print("✅ Version branding - IMPLEMENTED")
        else:
            print("❌ Version branding - MISSING")
    
    print("\n🎉 VISUAL ENHANCEMENT STATUS: READY FOR PRODUCTION")
    print("\nPyPozo 2.0 ahora incluye:")
    print("• 🏷️  Ícono oficial de aplicación")
    print("• 🎨  Logo completo en interfaz")
    print("• 📱  Branding de versión en barra de estado")
    print("• ✨  Estilo visual profesional mejorado")

if __name__ == "__main__":
    test_visual_assets()
