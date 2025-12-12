from groq import Groq
from django.conf import settings
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.LLM_MODEL
    
    def generate_response(self, query: str, context: List[str], 
                         chat_history: List[Dict] = None) -> str:
        """Generate response using RAG"""
        try:
            context_text = "\n\n".join(context) if context else "No relevant context found."
            
            system_message = f"""You are a helpful AI assistant. Answer the user's question based on the following context.

Context:
{context_text}

If the answer cannot be found in the context, say so politely and provide general knowledge if appropriate."""
            
            messages = [{"role": "system", "content": system_message}]
            
            if chat_history:
                messages.extend(chat_history[-5:])
            
            messages.append({"role": "user", "content": query})
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1024
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"Sorry, I encountered an error: {str(e)}"