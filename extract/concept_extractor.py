import logging
from process.llm_client import LLMEngine

class ConceptExtractor:
    def __init__(self):
        self.llm = LLMEngine()

    def extract_terms(self, article):
        logging.info(f"Extracting concepts from: {article.get('title', 'Unknown')}")
        
        system_instruction = (
            "You are a technical knowledge extractor. Identify 1-2 important AI concepts "
            "mentioned in the text. Return a JSON object with a key 'concepts' "
            "containing a list of objects with 'term' and 'context'."
        )
        
        prompt = f"Identify AI terms in this text: {article.get('content', '')[:3000]}"
        
        try:
            # Pass both arguments
            result = self.llm.generate_json(prompt, system_instruction)
            return result.get('concepts', []) if result else []
        except Exception as e:
            logging.error(f"Extraction failed: {e}")
            return []