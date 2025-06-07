"""
Multilingual AI Service for Language-Aware Responses

This service enhances the existing AI dialogue service with internationalization
support, providing contextually appropriate responses in the user's preferred language.
"""

import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from src.services.ai_dialogue_service import AIDialogueService
from src.services.translation_service import TranslationService
from src.models.user import User

logger = logging.getLogger(__name__)


class MultilingualAIService:
    """Enhanced AI service with language awareness and translation support"""
    
    def __init__(self, db: Session, ai_service: AIDialogueService, translation_service: TranslationService):
        self.db = db
        self.ai_service = ai_service
        self.translation_service = translation_service
    
    async def get_language_context(self, user_id: int) -> Dict[str, str]:
        """Get language context for AI responses"""
        try:
            # Get user's preferred language
            user_language = await self.translation_service.get_user_language_preference(user_id)
            
            # Get AI language context for the user's language
            ai_context = await self.translation_service.get_ai_language_context(user_language)
            
            return {
                "user_language": user_language,
                "ai_context": ai_context,
                "cultural_context": self._get_cultural_context(user_language)
            }
            
        except Exception as e:
            logger.error(f"Failed to get language context for user {user_id}: {e}")
            # Fallback to English
            return {
                "user_language": "en",
                "ai_context": "Respond in English with professional space trading terminology",
                "cultural_context": "western"
            }
    
    def _get_cultural_context(self, language_code: str) -> str:
        """Get cultural context for language-appropriate responses"""
        cultural_contexts = {
            'en': 'western',
            'es': 'hispanic',
            'zh-CN': 'chinese',
            'fr': 'french',
            'pt': 'brazilian',
            'de': 'german',
            'ja': 'japanese',
            'ru': 'russian',
            'ar': 'arabic',
            'ko': 'korean',
            'it': 'italian',
            'nl': 'dutch'
        }
        return cultural_contexts.get(language_code, 'western')
    
    async def generate_dialogue_response(
        self, 
        user_id: int,
        dialogue_context: Dict[str, Any],
        player_response: str
    ) -> Dict[str, Any]:
        """Generate AI dialogue response with language awareness"""
        try:
            # Get language context
            lang_context = await self.get_language_context(user_id)
            
            # Enhance dialogue context with language information
            enhanced_context = {
                **dialogue_context,
                "language_context": lang_context,
                "response_language": lang_context["user_language"],
                "cultural_awareness": self._get_cultural_guidelines(lang_context["user_language"])
            }
            
            # Generate response using enhanced context
            response = await self.ai_service.analyze_response_and_generate_follow_up(
                enhanced_context,
                player_response
            )
            
            # Add language metadata to response
            response["language_info"] = {
                "response_language": lang_context["user_language"],
                "cultural_context": lang_context["cultural_context"]
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to generate multilingual dialogue response: {e}")
            # Fallback to standard AI service
            return await self.ai_service.analyze_response_and_generate_follow_up(
                dialogue_context,
                player_response
            )
    
    def _get_cultural_guidelines(self, language_code: str) -> Dict[str, str]:
        """Get cultural guidelines for appropriate dialogue generation"""
        guidelines = {
            'en': {
                'tone': 'Professional and direct',
                'formality': 'Moderate',
                'humor': 'Subtle, dry humor acceptable',
                'authority': 'Respectful but not overly deferential'
            },
            'es': {
                'tone': 'Warm but professional',
                'formality': 'More formal than English',
                'humor': 'Light humor acceptable',
                'authority': 'Respectful and courteous'
            },
            'zh-CN': {
                'tone': 'Respectful and formal',
                'formality': 'High formality expected',
                'humor': 'Minimal, very subtle',
                'authority': 'Show proper respect for hierarchy'
            },
            'fr': {
                'tone': 'Elegant and articulate',
                'formality': 'Formal but not rigid',
                'humor': 'Sophisticated humor acceptable',
                'authority': 'Polite and respectful'
            },
            'ja': {
                'tone': 'Extremely polite and respectful',
                'formality': 'Very high formality',
                'humor': 'Very minimal, if any',
                'authority': 'Deep respect for authority'
            },
            'ar': {
                'tone': 'Respectful and dignified',
                'formality': 'Formal and courteous',
                'humor': 'Conservative, minimal',
                'authority': 'Show proper respect'
            }
        }
        
        return guidelines.get(language_code, guidelines['en'])
    
    async def get_localized_ship_descriptions(self, user_id: int) -> Dict[str, Dict[str, str]]:
        """Get ship descriptions in the user's preferred language"""
        try:
            user_language = await self.translation_service.get_user_language_preference(user_id)
            
            # Get ship-related translations
            ship_translations = await self.translation_service.get_namespace_translations(
                user_language, "game"
            )
            
            # Extract ship descriptions
            ships = ship_translations.get("ships", {})
            
            return {
                "scout": {
                    "name": ships.get("scout", "Scout Ship"),
                    "description": self._get_ship_description("scout", user_language)
                },
                "cargoHauler": {
                    "name": ships.get("cargoHauler", "Cargo Hauler"),
                    "description": self._get_ship_description("cargoHauler", user_language)
                },
                "lightFreighter": {
                    "name": ships.get("lightFreighter", "Light Freighter"),
                    "description": self._get_ship_description("lightFreighter", user_language)
                },
                "escapePod": {
                    "name": ships.get("escapePod", "Escape Pod"),
                    "description": self._get_ship_description("escapePod", user_language)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get localized ship descriptions: {e}")
            # Return English fallback
            return self._get_fallback_ship_descriptions()
    
    def _get_ship_description(self, ship_type: str, language_code: str) -> str:
        """Get detailed ship description for a specific language"""
        descriptions = {
            "en": {
                "scout": "A fast, nimble vessel perfect for reconnaissance and quick missions. Light armor but excellent speed and maneuverability.",
                "cargoHauler": "A robust cargo vessel designed for transporting large quantities of goods. Strong hull, moderate speed, good for trade missions.",
                "lightFreighter": "A balanced ship suitable for both combat and cargo transport. Versatile choice for new commanders.",
                "escapePod": "A minimal survival craft. Very limited capabilities but sufficient for basic transportation."
            },
            "es": {
                "scout": "Una nave rápida y ágil perfecta para reconocimiento y misiones rápidas. Blindaje ligero pero excelente velocidad y maniobrabilidad.",
                "cargoHauler": "Una nave de carga robusta diseñada para transportar grandes cantidades de mercancías. Casco resistente, velocidad moderada, buena para misiones comerciales.",
                "lightFreighter": "Una nave equilibrada adecuada tanto para combate como para transporte de carga. Elección versátil para nuevos comandantes.",
                "escapePod": "Una nave de supervivencia mínima. Capacidades muy limitadas pero suficientes para transporte básico."
            },
            "fr": {
                "scout": "Un vaisseau rapide et agile parfait pour la reconnaissance et les missions rapides. Blindage léger mais excellente vitesse et manœuvrabilité.",
                "cargoHauler": "Un vaisseau cargo robuste conçu pour transporter de grandes quantités de marchandises. Coque solide, vitesse modérée, bon pour les missions commerciales.",
                "lightFreighter": "Un vaisseau équilibré adapté au combat et au transport de fret. Choix polyvalent pour les nouveaux commandants.",
                "escapePod": "Un vaisseau de survie minimal. Capacités très limitées mais suffisantes pour le transport de base."
            },
            "zh-CN": {
                "scout": "一艘快速灵活的船只，完美适用于侦察和快速任务。装甲轻薄但速度和机动性出色。",
                "cargoHauler": "一艘坚固的货船，专为运输大量货物而设计。船体坚固，速度适中，适合贸易任务。",
                "lightFreighter": "一艘适合战斗和货物运输的平衡船只。新指挥官的多功能选择。",
                "escapePod": "一艘最小生存飞船。能力非常有限，但足以进行基本运输。"
            }
        }
        
        lang_descriptions = descriptions.get(language_code, descriptions["en"])
        return lang_descriptions.get(ship_type, "Ship description not available")
    
    def _get_fallback_ship_descriptions(self) -> Dict[str, Dict[str, str]]:
        """Fallback English ship descriptions"""
        return {
            "scout": {
                "name": "Scout Ship",
                "description": "A fast, nimble vessel perfect for reconnaissance and quick missions."
            },
            "cargoHauler": {
                "name": "Cargo Hauler",
                "description": "A robust cargo vessel designed for transporting large quantities of goods."
            },
            "lightFreighter": {
                "name": "Light Freighter",
                "description": "A balanced ship suitable for both combat and cargo transport."
            },
            "escapePod": {
                "name": "Escape Pod",
                "description": "A minimal survival craft with very limited capabilities."
            }
        }
    
    async def get_localized_game_messages(self, user_id: int, message_keys: list[str]) -> Dict[str, str]:
        """Get localized game messages for specific keys"""
        try:
            user_language = await self.translation_service.get_user_language_preference(user_id)
            
            # Get game translations
            game_translations = await self.translation_service.get_namespace_translations(
                user_language, "game"
            )
            
            result = {}
            for key in message_keys:
                # Support nested keys like "ai.greeting"
                value = game_translations
                for part in key.split('.'):
                    if isinstance(value, dict) and part in value:
                        value = value[part]
                    else:
                        value = key  # Fallback to key if not found
                        break
                result[key] = value
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get localized game messages: {e}")
            # Return keys as fallback
            return {key: key for key in message_keys}


# Service factory function
def get_multilingual_ai_service(
    db: Session,
    ai_service: AIDialogueService,
    translation_service: TranslationService
) -> MultilingualAIService:
    """Get multilingual AI service instance"""
    return MultilingualAIService(db, ai_service, translation_service)