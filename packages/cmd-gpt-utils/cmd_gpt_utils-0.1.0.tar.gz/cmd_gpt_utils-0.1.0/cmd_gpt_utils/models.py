from typing import List, Optional

from .config import Model
from .exceptions import ModelError

class ModelSelector:
    def __init__(self, models: List[Model]):
        if not models:
            raise ModelError("No models configured.")
        self.models = models

    def select(self, identifier: Optional[str] = None) -> Model:
        if not identifier:
            # Models are pre-sorted by id in ConfigLoader
            return self.models[0]

        try:
            model_id = int(identifier)
            for model in self.models:
                if model.id == model_id:
                    return model
            raise ModelError(f"No model found with id: {model_id}")
        except ValueError:
            # Identifier is a name, continue to prefix matching
            pass

        # First, check for an exact name match
        for model in self.models:
            if model.model_name == identifier:
                return model

        # If no exact match, fall back to prefix matching
        matched_models = [
            model for model in self.models 
            if model.model_name and model.model_name.startswith(identifier)
        ]

        if not matched_models:
            raise ModelError(f"No model found with name starting with: {identifier}")

        # Per clarification, return the one with the smallest id.
        # The list is already sorted by ID.
        return matched_models[0]
