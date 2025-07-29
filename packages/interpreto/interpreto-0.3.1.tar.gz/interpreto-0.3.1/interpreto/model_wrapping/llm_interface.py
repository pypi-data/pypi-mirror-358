# MIT License
#
# Copyright (c) 2025 IRT Antoine de Saint Exupéry et Université Paul Sabatier Toulouse III - All
# rights reserved. DEEL and FOR are research programs operated by IVADO, IRT Saint Exupéry,
# CRIAQ and ANITI - https://www.deel.ai/.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import annotations

# from abc import ABC, abstractmethod

# import torch


# # Abstract interface definition
# class LLMInterface(ABC):
#     @abstractmethod
#     def generate(self, system_prompt: str, user_prompt: str) -> str:
#         pass


# class HuggingFaceLLM(LLMInterface):  # TODO: use what we already have in nnsight
#     def __init__(self, model_name: str, device: str | torch.device | None = None):
#         try:
#             from transformers import AutoModelForCausalLM, AutoTokenizer
#         except ImportError as e:
#             raise ImportError("Install transformers and torch to use HuggingFace models.") from e

#         self.tokenizer = AutoTokenizer.from_pretrained(model_name)
#         self.model = AutoModelForCausalLM.from_pretrained(model_name)
#         self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
#         self.model.to(self.device)

#     def generate(self, system_prompt: str, user_prompt: str, max_new_tokens: int = 200) -> str:
#         prompt = f"{system_prompt}\n\nUser: {user_prompt}\nAssistant:"
#         inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
#         output_ids = self.model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=True)
#         output = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
#         return output[len(prompt) :].strip()


# class OpenAILLM(LLMInterface):
#     def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
#         try:
#             import openai
#         except ImportError as e:
#             raise ImportError("Install openai to use OpenAI API.") from e

#         openai.api_key = api_key
#         self.openai = openai
#         self.model = model

#     def generate(self, system_prompt: str, user_prompt: str) -> str:
#         response = self.openai.ChatCompletion.create(
#             model=self.model,
#             messages=[
#                 {"role": "system", "content": system_prompt},
#                 {"role": "user", "content": user_prompt},
#             ],
#         )
#         return response.choices[0].message.content.strip()


# class GoogleGeminiLLM(LLMInterface):
#     def __init__(self, api_key: str, model: str = "gemini-pro"):
#         try:
#             import google.generativeai as genai
#         except ImportError as e:
#             raise ImportError("Install google-generativeai to use Google Gemini API.") from e

#         genai.configure(api_key=api_key)
#         self.model = genai.GenerativeModel(model)

#     def generate(self, system_prompt: str, user_prompt: str) -> str:
#         prompt = f"{system_prompt}\n\n{user_prompt}"
#         response = self.model.generate_content(prompt)
#         return response.text.strip()


# class CohereLLM(LLMInterface):
#     def __init__(self, api_key: str, model: str = "command"):
#         try:
#             import cohere
#         except ImportError as e:
#             raise ImportError("Install cohere to use Cohere API.") from e

#         self.client = cohere.Client(api_key)
#         self.model = model

#     def generate(self, system_prompt: str, user_prompt: str) -> str:
#         prompt = f"{system_prompt}\n\n{user_prompt}"
#         response = self.client.generate(model=self.model, prompt=prompt)
#         return response.generations[0].text.strip()


# class AnthropicLLM(LLMInterface):
#     def __init__(self, api_key: str, model: str = "claude-3-haiku-20240307"):
#         try:
#             import anthropic
#         except ImportError as e:
#             raise ImportError("Install anthropic to use Anthropic API.") from e

#         self.client = anthropic.Anthropic(api_key=api_key)
#         self.model = model

#     def generate(self, system_prompt: str, user_prompt: str) -> str:
#         response = self.client.messages.create(
#             model=self.model,
#             system=system_prompt,
#             messages=[{"role": "user", "content": user_prompt}],
#             max_tokens=1024,
#         )
#         return response.content[0].text.strip()
