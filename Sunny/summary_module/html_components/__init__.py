"""
HTML Components for Learning Dashboard

This package contains modular HTML generators for different dashboard components.
"""

try:
    from .knowledge_diagram import KnowledgeDiagramGenerator
    from .content_cards import ContentCardsGenerator  
    from .quiz_interface import QuizInterfaceGenerator
    from .navigation import NavigationGenerator
    from .styles import StylesGenerator

    __all__ = [
        'KnowledgeDiagramGenerator',
        'ContentCardsGenerator', 
        'QuizInterfaceGenerator',
        'NavigationGenerator',
        'StylesGenerator'
    ]
except ImportError as e:
    print(f"Warning: Could not import all components: {e}")
    __all__ = []
