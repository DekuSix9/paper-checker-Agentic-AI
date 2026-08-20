import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")


import time

def call_groq_llm(
    prompt: str,
    system_prompt: str = "",
    model: Optional[str] = None,
    json_response: bool = False,
    retries: int = 2
) -> Optional[Any]:
    """
    Utility helper to call Groq API with automatic fallback and rate limit retry backoff.
    Returns parsed JSON dict if json_response=True, or string content, or None on failure.
    """
    groq_key = os.environ.get("GROQ_API_KEY")
    if not groq_key or groq_key == "your_groq_api_key_here":
        return None

    model = model or os.environ.get("GROQ_MODEL", "openai/gpt-oss-20b")

    for attempt in range(retries + 1):
        try:
            from groq import Groq
            client = Groq(api_key=groq_key)
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            request = {
                "model": model,
                "messages": messages,
                "temperature": 0.2,
                "max_tokens": 1600
            }
            if json_response:
                request["response_format"] = {"type": "json_object"}
            completion = client.chat.completions.create(**request)
            
            content = completion.choices[0].message.content or ""
            
            # Remove <think> ... </think> reasoning blocks if present (common in Qwen/DeepSeek models)
            import re
            content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
            
            if json_response:
                # Strip markdown codeblocks if present
                clean_content = content.strip()
                if "```json" in clean_content:
                    clean_content = clean_content.split("```json")[1].split("```")[0].strip()
                elif "```" in clean_content:
                    clean_content = clean_content.split("```")[1].split("```")[0].strip()
                
                try:
                    return json.loads(clean_content)
                except Exception as parse_err:
                    # Try finding first { and last }
                    start_idx = clean_content.find("{")
                    end_idx = clean_content.rfind("}")
                    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                        try:
                            return json.loads(clean_content[start_idx:end_idx+1])
                        except Exception:
                            pass
                    print(f"[groq_tools warning] Failed to parse JSON output: {parse_err}")
                    return None
                    
            return content
        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "rate_limit_exceeded" in err_str:
                if attempt < retries:
                    print(f"[groq_tools info] Rate limit 429 encountered. Retrying in 4s (attempt {attempt+1}/{retries})...")
                    time.sleep(4)
                    continue
            print(f"[groq_tools warning] Groq API call failed: {e}")
            return None
    return None
