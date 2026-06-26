import os
from typing import List, Optional, Type, TypeVar, Union, Any
from google import genai
from google.genai import types
from google.genai.errors import APIError 
from loguru import logger
from PIL import Image
from pydantic import BaseModel, ValidationError
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file


T = TypeVar('T', bound=BaseModel)
GEMINI_BASE_IMAGE_MODEL = "gemini-2.5-flash"
GEMINI_API_KEY = os.environ.get("GOOGLE_API_KEY")


class GeminiServiceError(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        original_error: Exception | None = None,
    ):
        self.message = message
        self.status_code = status_code
        self.original_error = original_error
        super().__init__(message)



#add try catch for APIError, and ohter errors, and return a meaningful error message
def text_to_text(
    input_text: str,
    system_prompt: Optional[str] = None,
    user_prompt: Optional[str] = None,
    must_include: Optional[List[str]] = None,
    must_exclude: Optional[List[str]] = None,
    api_key: Optional[str] = None,
    model: str = "gemini-2.5-flash",
    output_format: Optional[Type[T]] = None,
) -> Optional[T]:
    
    try:
        client = genai.Client(api_key=api_key)
        prompt = user_prompt or ""

        prompt += f"""

        Input:
        {input_text}
        """


        if must_include:
            prompt += f"""

            Must include:
            {", ".join(must_include)}
            """


        if must_exclude:
            prompt += f"""

        Must avoid:
        {", ".join(must_exclude)}
        """


        config_kwargs = {
            "system_instruction": system_prompt,
        }


        if output_format:
            config_kwargs["response_mime_type"] = "application/json"
            config_kwargs["response_schema"] = output_format


        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                **config_kwargs
            )
        )


        if not response.text:
            logger.error("Gemini returned an empty response.")
            raise GeminiServiceError(
                message="Our Support System is currently experiencing High Volume, Please try again later.",
                status_code=500,
                original_error=Exception("Empty response from Gemini")
            )

        if output_format:
            return output_format.model_validate_json(response.text)

        return response.text
    except ValidationError as e:
        logger.exception("Failed to parse Gemini response.")

        raise GeminiServiceError(
            message="Our Support System is currently experiencing High Volume, Please try again later.",
            original_error=e,
            status_code=500
        )

    except APIError as e:
        logger.error(f"API Error occurred: {e}")
        raise GeminiServiceError(message="Our Support System is currently experiencing High Volume, Please try again later.", status_code=500, original_error=e)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise GeminiServiceError(message="Our Support System is currently experiencing High Volume, Please try again later.", status_code=500, original_error=e)


def prompt_correction(
    prompt: str,
    improve_grammar: bool = True,
    improve_clarity: bool = True,
    optimize_for: Optional[str] = None,
    api_key: Optional[str] = None,
    model: str = "gemini-2.5-flash",
):

    instructions = """
You are a professional prompt engineer.
Improve the given prompt.
Return only the improved prompt.
"""


    if improve_grammar:
        instructions += """
Fix grammar mistakes.
"""


    if improve_clarity:
        instructions += """
Make the intent clearer and more specific.
"""
    if optimize_for:
        instructions += f"""
Optimize the prompt for: {optimize_for}
"""


    return text_to_text(
        input_text=prompt,
        system_prompt=instructions,
        api_key=api_key,
        model=model
    )

def translate_text(
    text: str,
    target_language: str,
    system_prompt: Optional[str] = None,
    user_prompt: Optional[str] = None,
    source_language: Optional[str] = None,
    api_key: Optional[str] = None,
    model: str = "gemini-2.5-flash",
    ):

    system = system_prompt or """
    You are a professional translator.
    Translate naturally while preserving meaning.
    """


    prompt = f"""
    Translate this text.

    Source language:
    {source_language or "auto detect"}

    Target language:
    {target_language}

    Text:
    {text}
    """


    if user_prompt:
        prompt += f"""

    Extra instruction:
    {user_prompt}
    """


    return text_to_text(
        input_text="",
        system_prompt=system,
        user_prompt=prompt,
        api_key=api_key,
        model=model
    )












