from .dialogs import NeuralCompletionDialog
from .neural_completion import NeuralCompletion

def create_completion_dialog(wells, parent=None):
    return NeuralCompletionDialog(wells, parent)
