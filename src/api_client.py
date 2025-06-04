#!/usr/bin/env python3
"""
API client for the AI Prompt Assistant.
Handles communication with the rephrasing API.
"""

import requests
import json
import urllib.parse
from history_manager import HistoryManager


class ApiClient:
    """Client for interacting with the rephrasing API."""
    
    def __init__(self, settings):
        """Initialize the API client with settings."""
        self.settings = settings
        self.history_manager = HistoryManager()
        self.base_url = "https://api.example.com"  # Replace with actual API URL
    
    def rephrase_prompt(self, text):
        """Send text to the rephrasing API and return the result."""
        endpoint = f"{self.base_url}/rephrase"
        ai_service = self.settings.get("ai_service", "chatgpt")
        
        payload = {
            "text": text,
            "target_ai": ai_service
        }
        
        try:
            response = requests.post(endpoint, json=payload, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            rephrased_text = result.get("rephrased_text", text)
            
            # Save to history
            self.history_manager.add_entry(text, rephrased_text, ai_service)
            
            return rephrased_text
            
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            # If API fails, return original text
            self.history_manager.add_entry(text, None, ai_service)
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
