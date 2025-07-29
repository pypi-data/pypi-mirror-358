import os

module_candidates = os.listdir(os.path.dirname(__file__))

module_candidates = [module_candidate[:-3]  # removing ".py" suffix
                     for module_candidate in module_candidates
                     if module_candidate.endswith(".py") and not module_candidate.startswith("_")]

module_candidates = [module_candidate for module_candidate in module_candidates if module_candidate.isidentifier()]

__all__ = module_candidates
