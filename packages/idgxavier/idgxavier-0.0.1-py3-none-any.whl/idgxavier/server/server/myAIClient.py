import os
from typeguard import typechecked
from typing import List, Dict, Optional, Union
from openai import OpenAI

from .. import constant as constX
from ..debugger import debugger
from .. import utils as utilsX

@typechecked
class myAIClient():
  def __init__(self, model: str) -> None:
    self.chatHistory: List[Dict[str, str]] = []
    self.model = model
    self.groqClient: Optional[OpenAI] = None

  def promptRemote(self, prompt: str, client: OpenAI) -> str:
    self.chatHistory = [{
      "role": "user",
      "content": prompt
    }]

    response = None
    text: Optional[str] = None
    try:
      response = client.chat.completions.create(
        messages=self.chatHistory,
        model=self.model,
        max_tokens=constX.MAX_OUTPUT_TOKENS,
        temperature=constX.TEMPERATURE
      )
    except Exception as e:
      debugger.error(f"[promptRemote] {e}\n\n\nOriginal Prompt:\n{prompt}")
      return ""

    text = response.choices[0].message.content
    if text is None:
      raise RuntimeError("[promptRemote] No text provided")

    return text

  def sendPrompt(self, prompt: str) -> str:
    utilsX.logInFiles("---------\nPrompt: " + prompt + "\n---------")
    if not self.groqClient:
      raise RuntimeError("Groq API key is not set. Please set the API key before making requests.")
    
    # OpenAI(
      # base_url="https://api.groq.com/openai/v1",
    # )

    text = self.promptRemote(prompt, self.groqClient)
    
    utilsX.logInFiles("\n--------response--------\n" + text)
    utilsX.logInFiles("--------finished--------")

    return text

  def initGroqClient(self, apiKey: str) -> None:
    self.groqClient = OpenAI(
      base_url="https://api.groq.com/openai/v1",
      api_key=apiKey
    )