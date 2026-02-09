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
            
            system_message = f"""You are a smart and helpful AI assistant. 
Your goal is to answer the user's question clearly and concisely based on the context provided.

GUIDELINES FOR RESPONSE:
1. **Structure**: Use bullet points, numbered lists, and bold headings to organize your answer.
2. **Clarity**: Avoid long, clumsy paragraphs. Break down information into digestable points.
3. **Accuracy**: Use the provided context as your primary source. **However, if the answer is not in the context, please answer using your general knowledge.**
4. **Formatting**: Use Markdown to make the text visually appealing (e.g., **bold** for key terms, `code` for technical terms).

Context:
{context_text}
"""
            
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