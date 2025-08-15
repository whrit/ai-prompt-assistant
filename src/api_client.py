#!/usr/bin/env python3
"""
API client for the AI Prompt Assistant.
Handles communication with the rephrasing API.
"""

import requests
import urllib.parse
import os
from src.history_manager import HistoryManager


class ApiClient:
    """Client for interacting with the rephrasing API."""
    
    def __init__(self, settings):
        """Initialize the API client with settings."""
        self.settings = settings
        self.history_manager = HistoryManager()
        # Using a free public API for text rephrasing
        self.base_url = "https://api.openai.com/v1"  # OpenAI API endpoint
        
        # API key would normally be stored securely and retrieved
        # For now, we'll check if it's in settings or use environment variable
        self.api_key = settings.get("openai_api_key", "") or os.environ.get("OPENAI_API_KEY", "")
    
    def rephrase_prompt(self, text):
        """Send text to the rephrasing API and return the result."""
        endpoint = f"{self.base_url}/chat/completions"
        ai_service = self.settings.get("ai_service", "chatgpt")
        
        # Check if we have an API key
        if not self.api_key:
            print("No API key available. Using original text.")
            # Store the original text in history
            self.history_manager.add_entry(text, text, ai_service)
            # Refresh API key in case it was just set
            self.api_key = self.settings.get("openai_api_key", "") or os.environ.get("OPENAI_API_KEY", "")
            if not self.api_key:
                # Still no API key, return original text
                return text
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # Create a prompt that asks to rephrase the text
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that rephrases 'how to' queries to make them more effective. Keep your response concise and only return the rephrased query without explanations or additional text."
                },
                {
                    "role": "user",
                    "content": f"Rephrase this query to make it more effective: '{text}'"
                }
            ],
            "temperature": 0.7,
            "max_tokens": 150
        }
        
        try:
            response = requests.post(endpoint, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            rephrased_text = result.get("choices", [{}])[0].get("message", {}).get("content", text).strip()
            
            # Save to history with both original and rephrased text
            self.history_manager.add_entry(text, rephrased_text, ai_service)
            
            print(f"Successfully rephrased: '{text}' to '{rephrased_text}'")
            return rephrased_text
            
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            # If API fails, save original text to history
            self.history_manager.add_entry(text, text, ai_service)
            # Return original text so the user can still use it
            return text
        except Exception as e:
            print(f"Unexpected error during API call: {e}")
            # For any other errors, save original text to history
            self.history_manager.add_entry(text, text, ai_service)
            # Return original text
            return text
    
    def get_ai_service_url(self, ai_service, prompt_text):
        """Get the URL for the specified AI service with the prompt."""
        # URL encode the prompt text
        encoded_text = urllib.parse.quote(prompt_text)
        
        # Map of AI services to their URLs
        service_urls = {
            "chatgpt": f"https://chat.openai.com/?prompt={encoded_text}",
            "bard": f"https://bard.google.com/?prompt={encoded_text}",
            "claude": f"https://claude.ai/chat?prompt={encoded_text}",
            # Add more services as needed
        }
        
        # Return the URL for the specified service, or ChatGPT as default
        return service_urls.get(ai_service, service_urls["chatgpt"])
