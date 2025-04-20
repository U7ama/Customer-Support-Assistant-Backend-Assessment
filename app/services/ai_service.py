import os
import json
import asyncio
import aiohttp
from typing import AsyncGenerator, Dict, List
from fastapi import HTTPException, status
from app.core.config import settings
from app.db.models import Message, Ticket

class AIService:
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.model = settings.GROQ_MODEL
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _build_prompt(self, ticket: Ticket, messages: List[Message]) -> str:
        """Build a prompt for the AI model based on ticket and message history"""
        # Get the message history
        message_history = "\n".join([
            f"{'Support Assistant' if msg.is_ai else 'Customer'}: {msg.content}"
            for msg in messages
        ])
        
        # Get the latest message (if any)
        latest_message = ""
        if messages and not messages[-1].is_ai:
            latest_message = messages[-1].content
        
        # Build the prompt
        prompt = f"""
        You are a helpful customer support assistant. 
        The customer has the following issue: {ticket.description}

        Previous messages:
        {message_history}

        {"Customer's latest message: " + latest_message if latest_message else ""}

        Provide a helpful response that addresses their concern:
        """
        
        return prompt
    
    async def generate_response(self, ticket: Ticket, messages: List[Message]) -> str:
        """Generate an AI response for a ticket using direct HTTP request"""
        prompt = self._build_prompt(ticket, messages)
        
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url, 
                    headers=self.headers, 
                    json=payload
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise HTTPException(
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Groq API error: {error_text}"
                        )
                    
                    result = await response.json()
                    return result["choices"][0]["message"]["content"]
        except aiohttp.ClientError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error communicating with Groq API: {str(e)}"
            )
    
    async def stream_response(self, ticket: Ticket, messages: List[Message]) -> AsyncGenerator[str, None]:
        """
        Stream an AI response for a ticket
        
        Note: This is a simplified version that doesn't use actual streaming.
        It generates the full response first, then simulates streaming by yielding chunks.
        """
        try:
            # Get the full response
            full_response = await self.generate_response(ticket, messages)
            
            # Simulate streaming by yielding chunks of the response
            chunk_size = 10  # characters per chunk
            for i in range(0, len(full_response), chunk_size):
                chunk = full_response[i:i+chunk_size]
                yield chunk
                await asyncio.sleep(0.05)  # Simulate delay between chunks
                
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error streaming AI response: {str(e)}"
            )

# Initialize the service
ai_service = AIService()