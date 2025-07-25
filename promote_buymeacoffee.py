"""
🎉 Script de promoción interactivo para Buy Me a Coffee
Muestra de forma atractiva las formas de apoyar PyPozo
"""

import sys
import time
import webbrowser
from datetime import datetime

def show_animated_banner():
    """Muestra un banner animado promocional."""
    
    banner_lines = [
        "╔══════════════════════════════════════════════════════════════════╗",
        "║                     ☕ APOYA A PYPOZO ☕                         ║", 
        "║                                                                  ║",
        "║  🚀 ¿Te gusta PyPozo? ¡Ayúdanos a seguir innovando!             ║",
        "║                                                                  ║",
        "║  💡 Tu apoyo significa:                                          ║",
        "║     ✅ Nuevas funcionalidades geofísicas                        ║",
        "║     ✅ Algoritmos de IA más avanzados                           ║", 
        "║     ✅ Soporte y actualizaciones continuas                      ║",
        "║     ✅ PyPozo gratuito para toda la comunidad                   ║",
        "║                                                                  ║",
        "║  🌟 Buy me a coffee: https://buymeacoffee.com/ingjoma           ║",
        "║                                                                  ║",
        "╚══════════════════════════════════════════════════════════════════╝"
    ]
    
    print("\n" + "🎵 " * 20)
    
    for line in banner_lines:
        print(line)
        time.sleep(0.1)
    
    print("🎵 " * 20 + "\n")

def show_donation_options():
    """Muestra las opciones de donación disponibles."""
    
    print("💖 OPCIONES DE APOYO:")
    print("=" * 50)
    
    options = [
        ("☕", "$3 USD", "Un café para seguir programando", "Básico"),
        ("🍕", "$10 USD", "Una pizza para largas sesiones", "Contribuidor"), 
        ("🚀", "$25 USD", "Combustible para nuevas funciones", "Patrocinador"),
        ("🏆", "$50+ USD", "Patrocinador Premium con beneficios", "Premium")
    ]
    
    for emoji, amount, description, tier in options:
        print(f"{emoji} {amount:8} - {description}")
        print(f"{'':12}   🏷️ Tier: {tier}")
        print()

def show_impact_stats():
    """Muestra estadísticas de impacto del proyecto."""
    
    print("📊 IMPACTO DE TU APOYO:")
    print("=" * 50)
    
    stats = [
        ("🔬", "Módulos principales", "Petrofísica, Geología, IA"),
        ("⏱️", "Desarrollo activo", "En constante evolución"),
        ("🌍", "Alcance global", "Open Source worldwide"),
        ("💾", "Líneas de código", "Creciendo continuamente"),
        ("🏆", "Calidad", "Alternativa profesional"),
        ("💡", "Innovación", "IA aplicada a geofísica")
    ]
    
    for emoji, metric, value in stats:
        print(f"{emoji} {metric:30} {value:>10}")
    
    print()

def show_success_stories():
    """Muestra historias de éxito y testimonios."""
    
    print("🌟 HISTORIAS DE ÉXITO:")
    print("=" * 50)
    
    testimonials = [
        {
            "user": "Desarrollador PyPozo",
            "text": "Este proyecto nació de la necesidad de herramientas geofísicas accesibles",
            "emoji": "💡"
        },
        {
            "user": "Visión del proyecto",
            "text": "Democratizar el análisis geofísico con herramientas de calidad profesional",
            "emoji": "�"
        },
        {
            "user": "Comunidad open source",
            "text": "Juntos podemos construir la mejor alternativa libre a software comercial",
            "emoji": "🤝"
        }
    ]
    
    for story in testimonials:
        print(f"{story['emoji']} \"{story['text']}\"")
        print(f"   - {story['user']}")
        print()

def interactive_support_menu():
    """Menú interactivo para opciones de apoyo."""
    
    while True:
        print("\n🎯 ¿CÓMO QUIERES APOYAR PYPOZO?")
        print("=" * 40)
        print("1. 💰 Abrir Buy Me a Coffee")
        print("2. 📢 Compartir en redes sociales") 
        print("3. ⭐ Dar estrella en GitHub")
        print("4. 📊 Ver impacto del proyecto")
        print("5. 🌟 Leer historias de éxito")
        print("6. 🚀 Continuar usando PyPozo")
        print("0. ❌ Salir")
        
        try:
            choice = input("\n👉 Elige una opción (0-6): ").strip()
            
            if choice == "1":
                print("🌐 Abriendo Buy Me a Coffee...")
                webbrowser.open("https://buymeacoffee.com/ingjoma")
                print("✅ ¡Gracias por considerar apoyar PyPozo!")
                
            elif choice == "2":
                print("📱 URLs para compartir:")
                print("🐦 Twitter: 'Descubre #PyPozo - Análisis geofísico gratuito y profesional! https://buymeacoffee.com/ingjoma'")
                print("💼 LinkedIn: 'PyPozo está revolucionando el análisis petrofísico con IA. ¡Apoya este proyecto increíble!'")
                print("📘 Facebook: 'Software geofísico gratuito que compite con soluciones comerciales de miles de dólares'")
                
            elif choice == "3":
                print("🌐 Abriendo repositorio de GitHub...")
                webbrowser.open("https://github.com/JoseMariaGarciaMarquez/pypozo")
                print("⭐ ¡No olvides dar estrella al repositorio!")
                
            elif choice == "4":
                show_impact_stats()
                
            elif choice == "5":
                show_success_stories()
                
            elif choice == "6":
                print("🚀 ¡Perfecto! Que tengas un excelente análisis con PyPozo")
                print("💡 Recuerda: tu apoyo hace posible el desarrollo continuo")
                break
                
            elif choice == "0":
                print("👋 ¡Hasta pronto! Gracias por usar PyPozo")
                break
                
            else:
                print("❌ Opción no válida. Intenta de nuevo.")
                
        except KeyboardInterrupt:
            print("\n👋 ¡Hasta pronto!")
            break
        except Exception:
            print("❌ Error en la entrada. Intenta de nuevo.")

def main():
    """Función principal del script promocional."""
    
    print("🎉 PROMOCIÓN PYPOZO - BUY ME A COFFEE")
    print("=" * 60)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Banner animado
    show_animated_banner()
    
    # Opciones de donación
    show_donation_options()
    
    # Menú interactivo
    interactive_support_menu()

if __name__ == "__main__":
    main()
