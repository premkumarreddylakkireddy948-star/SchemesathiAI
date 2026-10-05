import os
import logging
from typing import List, Dict, Any, Optional
from app.config import settings

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.api_key = settings.effective_llm_key

    def is_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key.strip()) > 5)

    def generate_response(self, system_prompt: str, user_message: str, context_chunks: List[Dict[str, Any]] = None) -> str:
        """
        Generate grounded response using LLM (Gemini or LangChain fallback)
        """
        key = self.api_key or settings.effective_llm_key
        
        # Prepare context grounding
        context_str = ""
        if context_chunks:
            context_str = "\n\n--- GROUNDING KNOWLEDGE BASE CHUNKS ---\n"
            for i, chunk in enumerate(context_chunks, 1):
                payload = chunk.get("payload", {})
                context_str += (
                    f"[{i}] SCHEME: {payload.get('scheme_name', 'Unknown')}\n"
                    f"DOCUMENT: {payload.get('document_name', 'Unknown')}\n"
                    f"CATEGORY: {payload.get('category', 'General')}\n"
                    f"CONTENT: {payload.get('text', '')}\n"
                    f"SOURCE URL: {payload.get('source_url', 'N/A')}\n\n"
                )

        full_user_prompt = f"{user_message}\n{context_str}" if context_str else user_message

        # Try Google Gemini API if key is available
        if key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=key)
                model = genai.GenerativeModel("gemini-1.5-flash")
                prompt = f"{system_prompt}\n\nUser Question:\n{full_user_prompt}"
                response = model.generate_content(prompt)
                if response and response.text:
                    return self._enforce_eligibility_disclaimer(response.text)
            except Exception as e:
                logger.warning(f"Google Generative AI call failed ({e}). Falling back to grounded rule engine.")

        # High-quality grounded reasoning synthesis engine
        return self._generate_grounded_fallback(user_message, context_chunks)

    def _generate_grounded_fallback(self, query: str, context_chunks: List[Dict[str, Any]]) -> str:
        """
        Synthesizes grounded response from retrieved knowledge chunks
        """
        if not context_chunks:
            return (
                "I searched the official scheme knowledge base, but couldn't find specific matching "
                "guidelines for your query. Please browse the **Scheme Explorer** or refine your search parameters."
            )

        schemes_found = {}
        for chunk in context_chunks:
            payload = chunk.get("payload", {})
            sname = payload.get("scheme_name", "Government Scheme")
            if sname not in schemes_found:
                schemes_found[sname] = {
                    "doc": payload.get("document_name", ""),
                    "category": payload.get("category", ""),
                    "texts": [],
                    "url": payload.get("source_url", "")
                }
            schemes_found[sname]["texts"].append(payload.get("text", ""))

        # Check if query is targeting a specific scheme
        q_lower = query.lower()
        target_kws = []
        if "kisan" in q_lower or "kissan" in q_lower or "pmkisan" in q_lower:
            target_kws.append("kisan")
        if "ayushman" in q_lower or "pmjay" in q_lower or "pm-jay" in q_lower:
            target_kws.append("ayushman")
            target_kws.append("pm-jay")
        if "pmay" in q_lower or "awas" in q_lower:
            target_kws.append("awas")
            target_kws.append("pmay")
        if "stand up" in q_lower or "standup" in q_lower:
            target_kws.append("stand up")
        if "post-matric" in q_lower:
            target_kws.append("post-matric")

        if target_kws:
            filtered = {}
            for sname, details in schemes_found.items():
                s_low = sname.lower()
                d_low = details["doc"].lower()
                if any(kw in s_low or kw in d_low for kw in target_kws):
                    filtered[sname] = details
            if filtered:
                schemes_found = filtered

        response = "Based on official government scheme guidelines retrieved from our knowledge base, here are potentially relevant options for your situation:\n\n"

        for sname, details in schemes_found.items():
            response += f"### 📌 {sname}\n"
            response += f"**Category:** {details['category']}\n\n"
            
            # Key highlights
            combined_text = "\n".join(details['texts'])
            
            # Extract eligibility notes
            response += f"**Why it appears relevant:**\n"
            response += f"Based on the information provided, this scheme appears potentially relevant because official guidelines indicate coverage for eligible beneficiaries meeting specified criteria in {details['category']}.\n\n"
            
            # Snippet excerpt
            excerpt = combined_text[:350].strip()
            if len(combined_text) > 350:
                excerpt += "..."
            response += f"**Official Details Excerpt:**\n> {excerpt}\n\n"

        response += (
            "--- \n"
            "⚠️ **Important Disclaimer:** Final eligibility, quota availability, and benefit sanctioning "
            "must be verified with the official government department or competent revenue authority."
        )

        return response

    def _enforce_eligibility_disclaimer(self, text: str) -> str:
        # Guarantee strict adherence to prompt guidelines
        text = text.replace("You are eligible.", "Based on the information provided, this scheme appears potentially relevant because...")
        text = text.replace("You are fully eligible", "Based on the information provided, this scheme appears potentially relevant because...")
        if "final eligibility must be verified" not in text.lower():
            text += "\n\n*Note: Final eligibility must be verified with the official government authority.*"
        return text

llm_service = LLMService()
