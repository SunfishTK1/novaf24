# fast_api_create_reports.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uuid
import os
import logging
from io import BytesIO

from create_reports_class import ConversationReport

app = FastAPI()

class Transcript(BaseModel):
    transcript: str

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/generate_report")
async def generate_report(transcript_data: Transcript):
    try:
        # Instantiate the ConversationReport with the transcript
        report = ConversationReport(transcript=transcript_data.transcript)
        
        # Analyze the transcript
        await report.analyze_transcript_with_gpt()
        
        # Generate the PDF report into an in-memory buffer
        pdf_buffer = BytesIO()
        report.generate_full_report(pdf_buffer)
        pdf_buffer.seek(0)
        
        # Validate PDF creation by checking buffer size
        if pdf_buffer.getbuffer().nbytes < 1000:
            logger.error("Generated PDF is too small or invalid.")
            raise HTTPException(
                status_code=500,
                detail="Failed to generate a valid PDF report."
            )
        
        # Return the PDF as a streaming response
        return StreamingResponse(
            pdf_buffer,
            media_type='application/pdf',
            headers={'Content-Disposition': 'attachment; filename=scam_report.pdf'}
        )
        
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while generating the report.")