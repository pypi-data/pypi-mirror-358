import os
from typing import Any

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI


from agentsociety.utils import load_api_key

DEFAULT_OPENAI_MODEL_KEY = "gpt-4o-2024-11-20"
DEFAULT_OPENAI_LRM_MODEL_KEY = "o1-mini"
DEFAULT_GROQ_MODEL_KEY = "llama3-70b-8192"
DEFAULT_GEMINI_MODEL_KEY = "gemini-1.5-pro-latest"

def load_openai_key():
    """
    Generates the interface to work with
    """
    api_key = load_api_key('openai_key')
    os.environ["OPENAI_API_KEY"] = api_key


def load_groq_key():
    """
    Generates the interface to work with
    """
    api_key = load_api_key('groq_key')
    os.environ["GROQ_API_KEY"] = api_key


def load_google_key():
    """
    Generates the interface to work with
    """
    api_key = load_api_key('google_key')
    os.environ["GOOGLE_API_KEY"] = api_key


def load_template_txt(name: str) -> str:
    """
    Loads the txt template
    """
    with open(f"../templates/{name}.txt", "r", encoding='utf-8') as f:
        return f.read()

def load_template_md(name: str) -> str:
    """
    Loads the MD template
    """
    with open(f"../templates/{name}.md", "r", encoding='utf-8') as f:
        return f.read()

class LLMSupplier:

    def make_llm(self, temperature: float, max_tokens: int) -> BaseChatModel:
        pass

class LRMSupplier:
    
    def make_lrm(self, max_tokens: int, model_key: str) -> BaseChatModel:
        pass


class OpenAiSupplier(LLMSupplier):

    def make_llm(self, temperature: float, max_tokens: int, model_key=DEFAULT_OPENAI_MODEL_KEY) -> BaseChatModel:
        load_openai_key()
        return ChatOpenAI(model=model_key, temperature=temperature, max_tokens=max_tokens)

class OpenAiLrmSupplier(LRMSupplier):

    def make_lrm(self, max_tokens: int, model_key: str = DEFAULT_OPENAI_LRM_MODEL_KEY):
        load_openai_key()
        return ChatOpenAI(model=model_key, temperature=1.0, max_tokens=max_tokens)

class GroqSupplier(LLMSupplier):

    def __init__(self, model: str = DEFAULT_GROQ_MODEL_KEY) -> None:
        super().__init__()
        self.model = model

    def make_llm(self, temperature: float, max_tokens: int) -> BaseChatModel:
        load_groq_key()
        return ChatGroq(model=self.model, temperature=temperature, max_tokens=max_tokens)


class GeminiSupplier(LLMSupplier):

    def __init__(self, model: str = DEFAULT_GEMINI_MODEL_KEY) -> None:
        super().__init__()
        self.model = model
    
    def make_llm(self, temperature: float, max_tokens: int) -> BaseChatModel:
        load_google_key()
        return ChatGoogleGenerativeAI(model=self.model, temperature=temperature, max_output_tokens=max_tokens)


LLM_SUPPLIER = None

def get_llm_supplier() -> LLMSupplier:
    global LLM_SUPPLIER
    if LLM_SUPPLIER is None:
        llm_supplier_str = os.getenv("LLM_SUPPLIER", "OPENAI")

        match llm_supplier_str:
            case "OPENAI":
                LLM_SUPPLIER = OpenAiSupplier()
            case "GROQ-llama3-70B":
                LLM_SUPPLIER = GroqSupplier()
            case "GROQ-gemma-7b-it":
                LLM_SUPPLIER = GroqSupplier(model='gemma-7b-it')
            case "GROQ-mixtral-8x7b":
                LLM_SUPPLIER = GroqSupplier(model='mixtral-8x7b-32768')
            case 'GEMINI':
                LLM_SUPPLIER = GeminiSupplier()
            case _:
                raise RuntimeError(f"Can't find an LLM supplier for key '{llm_supplier_str}'")
    return LLM_SUPPLIER

LRM_SUPPLIER = None

def get_lrm_supplier() -> LRMSupplier:
    global LRM_SUPPLIER
    if LRM_SUPPLIER is None:
        lrm_supplier_str = os.getenv("LRM_SUPPLIER", "OPENAI")
        
        match lrm_supplier_str:
            case "OPENAI":
                LRM_SUPPLIER = OpenAiLrmSupplier()
            case _:
                raise RuntimeError(f"Can't find a reasoning model for key '{lrm_supplier_str}'")
    return LRM_SUPPLIER

def create_generic_template() -> PromptTemplate:
    template_text = load_template_txt("generic_template")
    return PromptTemplate(template=template_text, input_variables=["chat_history"], template_format='jinja2')


def create_generic_chain(long: bool = True) -> LLMChain:
    model = get_llm_supplier().make_llm(temperature=0.2, max_tokens=2048 if long else 10)
    return LLMChain(llm=model, prompt=create_generic_template())
