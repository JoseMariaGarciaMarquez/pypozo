# Integración de PozoChatWindow para la app principal
_pozochat_available = False
try:
    from pozochat.pozochat_gui import PozoChatWindow
    _pozochat_available = True
except Exception:
    pass
POZOCHAT_AVAILABLE = _pozochat_available
