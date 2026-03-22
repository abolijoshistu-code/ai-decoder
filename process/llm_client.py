import os
import json
import logging
from google import genai
from google.genai import types
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()

class LLMEngine:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env")
        
        # Initialize client
        self.client = genai.Client(api_key=api_key)
        
        # Using Gemini 2.5 Flash: more stable and faster for the new SDK
        self.model_id = "gemini-2.5-flash"
        logging.info(f"LLMEngine initialized with: {self.model_id}")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=4, max=60))
    def generate_json(self, prompt, system_instruction):
        """
        Generic JSON generator using the modern SDK.
        """
        try:
            # Note: We pass just the ID string; the SDK handles the 'models/' prefix internally
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    temperature=0.1
                )
            )
            
            if not response or not response.text:
                logging.warning(f"Empty response from {self.model_id}")
                return None
                
            return json.loads(response.text)
            
        except Exception as e:
            # If 404 persists, it may be a regional restriction on 2.0-flash
            logging.error(f"LLM Logic Error: {e}")
            raise e

    def get_structured_concept(self, term, context="General AI context"):
        """Decodes terms for the Jargon Decoder search/pipeline."""
        sys_msg = (
            "You are an AI Jargon Decoder. Return a JSON object with: "
            "title, summary, explanation, analogy, example. Tone: ELI5."
        )
        user_msg = f"Decode this term: '{term}'. Context: {context}"
        return self.generate_json(user_msg, sys_msg)