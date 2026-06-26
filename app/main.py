from http.client import HTTPException
import os
from app.config.const import system_prompts_for_analyze_ticket
from app.models import AnalyzeTicketRequest, AnalyzeTicketResponse
#loguru
from app.utils.google_ai import GeminiServiceError, text_to_text, translate_text
from app.utils.utils_method import request_to_prompt
from loguru import logger
#import logging
from fastapi import FastAPI



# from app.router.ai import router as ai_router 



app = FastAPI(
    title="AI Backend"
)
# app.include_router(
#     ai_router,
#     prefix="/api"
# )

@app.get("/")
async def root():
    return {"message": "App is running!"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}


#system prompt for translation

#ticket analyze api endpoint 
@app.post("/analyze-ticket")
async def analyze_ticket(request: AnalyzeTicketRequest):
    try:
        # Here you would implement the logic to analyze the ticket using your AI model.
        logger.info(f"Received ticket for analysis: {request}")
        input_language = request.language.value if request.language else "en"
        #req.complaint should trnslate to english if not in english
        logger.info(f"Input complaint: {request.complaint}")
        print(f"Input language: {input_language}")


        if input_language != "en":
            # Translate the complaint to English using your translation model
            translated_complaint = translate_text(
                text=request.complaint,
                source_language=input_language,
                target_language="en",
                system_prompt="You are a helpful assistant. Translate the following text to English.User may be enter mix of english and other language. Please translate the text to english. If the text is already in english, please return the same text.",
                user_prompt="Translate the following text to English}",
                model="gemini-3.5-flash",
                api_key=os.environ.get("GOOGLE_API_KEY")
            )
            logger.info(f"Translated complaint: {translated_complaint}")
            request.complaint = translated_complaint

        request_string= request_to_prompt(request)
        logger.info(f"Request string for AI model: {type(request_string)}")

        ai_response = text_to_text(
            input_text=request_string,
            model="gemini-2.5-flash",
            system_prompt=system_prompts_for_analyze_ticket,
            api_key=os.environ.get("GOOGLE_API_KEY"),
            output_format=AnalyzeTicketResponse
        )

        return ai_response
    except GeminiServiceError as e:

        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )

