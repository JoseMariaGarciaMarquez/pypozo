"""
Loader for Patreon DLC modules. Exposes all premium features in a modular way.
"""

import importlib
import sys
import types
from pathlib import Path

class DLCNamespace(types.SimpleNamespace):
    pass

def load_patreon_features():
    dlc = DLCNamespace()
    # Exponer los entry points principales como atributos directos
    try:
        import patreon_dlc.completion as completion
        dlc.create_completion_dialog = completion.create_completion_dialog
    except Exception:
        dlc.create_completion_dialog = None
    try:
        import patreon_dlc.statistics as statistics
        dlc.statistics = statistics
    except Exception:
        dlc.statistics = None
    try:
        import patreon_dlc.lithology as lithology
        dlc.lithology = lithology
    except Exception:
        dlc.lithology = None
    try:
        import patreon_dlc.fluids as fluids
        dlc.fluids = fluids
    except Exception:
        dlc.fluids = None
    try:
        import patreon_dlc.models as models
        dlc.models = models
    except Exception:
        dlc.models = None
    try:
        import patreon_dlc.shared as shared
        dlc.shared = shared
    except Exception:
        dlc.shared = None
    return dlc
