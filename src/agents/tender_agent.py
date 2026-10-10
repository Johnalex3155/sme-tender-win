
import json
import requests

class TenderAgent:
    def __init__(self, profile_path, llm_config=None):
        with open(profile_path, "r") as f:
            self.profile = json.load(f)
        
        self.llm_config = llm_config or {}
        self.api_key = self.llm_config.get("api_key")
        self.api_url = self.llm_config.get("api_url", "http://localhost:11434/api/generate")
        self.model = self.llm_config.get("model", "gemma2")

    @staticmethod
    def get_available_models(api_url, api_key):
        """Fetches available models from the Ollama API."""
        try:
            base_url = api_url.rstrip('/')
            if '/api/chat' in base_url:
                tags_url = base_url.replace('/api/chat', '/api/tags')
            elif '/api/generate' in base_url:
                tags_url = base_url.replace('/api/generate', '/api/tags')
            else:
                tags_url = f"{base_url}/api/tags"

            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"} if api_key else {}
            response = requests.get(tags_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])
                return [m.get("name") for m in models]
        except Exception as e:
            print(f"Error fetching models: {e}")
        return []

    def _call_llm(self, prompt):
        try:
            if self.api_key:
                chat_url = self.api_url.replace("/api/generate", "/v1/chat/completions") if "/api/generate" in self.api_url else self.api_url
                if "/v1" not in chat_url:
                    chat_url = chat_url.rstrip("/") + "/v1/chat/completions"

                response = requests.post(
                    chat_url,
                    headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.1
                    },
                    timeout=30
                )
                if response.status_code == 200:
                    return response.json()['choices'][0]['message']['content'].strip()
            else:
                response = requests.post(
                    self.api_url,
                    json={"model": self.model, "prompt": prompt, "stream": False},
                    timeout=30
                )
                if response.status_code == 200:
                    return response.json().get("response", "").strip()
        except Exception as e:
            print(f"LLM Connection Error: {e}")
        return None

    def is_valid_tender_content(self, text):
        text_lower = text.lower()
        hard_blocks = ["unusual traffic", "detected unusual traffic", "robot", "captcha", "verify you are human", "access denied", "cloudfare", "our systems have detected"]
        if any(indicator in text_lower for indicator in hard_blocks):
            return False, "Critical Error: Google has blocked the request (Bot Detection)."
        search_indicators = ["search results", "google.com/search", "did you mean", "results for"]
        if any(indicator in text_lower for indicator in search_indicators):
            return False, "Error: The agent extracted a search results page instead of the actual tender document."
        cookie_indicators = ["cookies", "consent", "terms of service", "privacy policy"]
        if any(indicator in text_lower for indicator in cookie_indicators):
            tender_keywords = ["bid", "tender", "requirement", "specification", "contract", "proposal"]
            if not any(keyword in text_lower for keyword in tender_keywords):
                return False, "The extracted content is a cookie consent or privacy page."
        return True, ""

    def analyze_win_probability(self, tender_text):
        is_valid, error_msg = self.is_valid_tender_content(tender_text)
        if not is_valid:
            return {"probability": "N/A", "justification": error_msg}

        prompt = f"Analyze this tender against the SME profile. SME Profile: {json.dumps(self.profile, indent=2)} Tender Text: {tender_text[:4000]}"
        result = self._call_llm(prompt)
        if result:
            try:
                return json.loads(result.strip().strip('`').replace('json', '', 1).strip())
            except:
                pass
        return self._heuristic_analysis(tender_text)

    def generate_proposal_draft(self, tender_text):
        is_valid, error_msg = self.is_valid_tender_content(tender_text)
        if not is_valid:
            return {"technical_approach": f"❌ {error_msg}", "checklist": []}

        prompt = f"Draft a technical approach and checklist. SME Profile: {json.dumps(self.profile, indent=2)} Tender Text: {tender_text[:4000]}"
        result = self._call_llm(prompt)
        if result:
            try:
                return json.loads(result.strip().strip('`').replace('json', '', 1).strip())
            except:
                pass
        return self._heuristic_proposal(tender_text)

    def _heuristic_analysis(self, tender_text):
        return {"probability": "30%", "justification": "Low alignment with SME capabilities."}

    def _heuristic_proposal(self, tender_text):
        return {"technical_approach": "Standard approach", "checklist": ["Registration", "Tax"]}
