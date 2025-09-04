from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import FileResponse, JSONResponse
from ai_agent import ask_agent
from speech_to_text import transcribe_with_groq
from text_to_speech import text_to_speech_with_gtts
import os
import uuid
import base64
from fastapi.middleware.cors import CORSMiddleware
import app_globals

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or put your frontend URL instead of "*"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Uploads directory for audio and images
UPLOAD_DIR = "uploads"
IMAGE_DIR = "images"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(IMAGE_DIR, exist_ok=True)

def cleanup_file(file_path: str):
    """Safely delete a file if it exists"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"Error deleting file {file_path}: {e}")

# Global variable to store uploaded image path for tools to access
uploaded_image_path = None

@app.post("/ask")
async def ask_question(
    audio: UploadFile = None, 
    text: str = Form(None),
    image: UploadFile = None
):
    
    audio_file_path = None
    image_file_path = None
    
    try:
        user_input = ""
        
        # Process audio if provided
        if audio:
            audio_file_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}.wav")
            with open(audio_file_path, "wb") as f:
                f.write(await audio.read())

            user_input = transcribe_with_groq(audio_file_path)
        
        # Process text if provided
        if text:
            user_input = text if not user_input else f"{user_input} {text}"
        
        # Process image if provided - store path globally for tools to access
        if image:
            image_file_path = os.path.join(IMAGE_DIR, f"{uuid.uuid4()}.jpg")
            with open(image_file_path, "wb") as f:
                f.write(await image.read())
            
            # Set global variable so your tools can access this image
            app_globals.uploaded_image_path = image_file_path
            print(app_globals.uploaded_image_path)
        
        # Ensure we have some input
        if not user_input and not image:
            return JSONResponse(
                {"error": "No input provided (text, audio, or image required)"}, 
                status_code=400
            )
        
        # If only image provided, use default prompt
        if not user_input and image:
            user_input = "What do you see in this image?"

        # Get AI response using your existing agent
        response = ask_agent(user_query=user_input)
        print("AI Response:", response)

        # Convert response to speech
        audio_file = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}.mp3")
        text_to_speech_with_gtts(response, audio_file, play_locally=False)
        
        # Clean up temporary files
        if audio_file_path:
            cleanup_file(audio_file_path)
        if image_file_path:
            cleanup_file(image_file_path)
            uploaded_image_path = None  # Clear the global variable

        return {
            "user_input": user_input,
            "response": response,
            "audio_url": f"/get-audio/{os.path.basename(audio_file)}",
            "had_image": image is not None
        }

    except Exception as e:
        # Clean up files in case of error
        if audio_file_path:
            cleanup_file(audio_file_path)
        if image_file_path:
            cleanup_file(image_file_path)
            app_globals.uploaded_image_path = None
        
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/get-audio/{filename}")
async def get_audio(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    return FileResponse(file_path, media_type="audio/mpeg")

# Optional: Clean up old audio files
@app.delete("/cleanup-audio")
async def cleanup_old_audio():
    """Clean up old audio files (call this periodically or via cron job)"""
    try:
        count = 0
        for filename in os.listdir(UPLOAD_DIR):
            file_path = os.path.join(UPLOAD_DIR, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
                count += 1
        
        return {"message": f"Cleaned up {count} audio files"}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)