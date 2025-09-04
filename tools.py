# import cv2
# import base64
# from dotenv import load_dotenv
# import time
# import app_globals
# import os



# load_dotenv()


# def capture_image():
#     frame = app_globals.last_frame 
#     if frame is None:
#         raise RuntimeError("No frame available. Start the camera first.")

#     # Encode frame as JPEG
#     ret, buffer = cv2.imencode(".jpg", frame)
#     if not ret:
#         raise RuntimeError("Failed to encode frame.")

#     # Return as base64 string if needed
#     return base64.b64encode(buffer).decode("utf-8")



# # def capture_image() -> str:
# #     """
# #     Captures one frame from the default webcam, resizes it,
# #     encodes it as Base64 JPEG (raw string) and returns it.
# #     """
# #     for idx in range(10):
# #         # cap = cv2.VideoCapture(idx, cv2.CAP_AVFOUNDATION)
# #         cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)   # Windows recommended backend

# #         if cap.isOpened():
# #             time.sleep(3)
# #             for _ in range(10):  # Warm up
# #                 cap.read()
# #             ret, frame = cap.read()
# #             cap.release()
# #             if not ret:
# #                 continue
# #             # cv2.imwrite("sample.jpg", frame)  # Optional
# #             ret, buf = cv2.imencode('.jpg', frame)
# #             if ret:
# #                 return base64.b64encode(buf).decode('utf-8')
# #     raise RuntimeError("Could not open any webcam (tried indices 0-3)")

# if app_globals.uploaded_image_path and os.path.exists(app_globals.uploaded_image_path):
#             print(f"Using uploaded image: {app_globals.uploaded_image_path}")
            
#             # Convert uploaded image file to base64
#             with open(app_globals.uploaded_image_path, "rb") as image_file:
#                 img_b64 = base64.b64encode(image_file.read()).decode('utf-8')

# from groq import Groq

# def analyze_image_with_query(query: str) -> str:
    
#     """
#     Expects a string with 'query'.
#     Captures the image and sends the query and the image to
#     to Groq's vision chat API and returns the analysis.
#     """
#     # img_b64 = app_globals.uploaded_image_path
#     model="meta-llama/llama-4-maverick-17b-128e-instruct"
    
#     if not query or not img_b64:
#         return "Error: both 'query' and 'image' fields required."

#     client=Groq()  
#     messages=[
#         {
#             "role": "user",
#             "content": [
#                 {
#                     "type": "text", 
#                     "text": query
#                 },
#                 {
#                     "type": "image_url",
#                     "image_url": {
#                         "url": f"data:image/jpeg;base64,{img_b64}",
#                     },
#                 },
#             ],
#         }]
#     chat_completion=client.chat.completions.create(
#         messages=messages,
#         model=model
#     )
    
#     return chat_completion.choices[0].message.content

# # query = "what is in the hand of the guy ?"
# # print(analyze_image_with_query(query))

import cv2
import base64
from dotenv import load_dotenv
import time
import app_globals
import os
from langchain_core.tools import tool

load_dotenv()

def capture_image():
    frame = app_globals.last_frame
    
    if frame is None:
        raise RuntimeError("No frame available. Start the camera first.")
    
    # Encode frame as JPEG
    ret, buffer = cv2.imencode(".jpg", frame)
    if not ret:
        raise RuntimeError("Failed to encode frame.")
    
    # Return as base64 string if needed
    return base64.b64encode(buffer).decode("utf-8")

from groq import Groq

@tool
def analyze_image_with_query(query: str) -> str:
    """
    Analyze an image based on the user's query.
    First checks for uploaded image, then falls back to webcam capture.
    
    Args:
        query: The question or analysis request about the image
    
    Returns:
        str: Analysis results from the AI model
    """
    
    try:
        img_b64 = None
        
        # Check if there's an uploaded image first
        if app_globals.uploaded_image_path and os.path.exists(app_globals.uploaded_image_path):
            print(f"Using uploaded image: {app_globals.uploaded_image_path}")
            
            # Convert uploaded image file to base64
            with open(app_globals.uploaded_image_path, "rb") as image_file:
                img_b64 = base64.b64encode(image_file.read()).decode('utf-8')
                
        else:
            print("No uploaded image found, trying webcam capture...")
            
            # Fall back to webcam capture (your existing logic)
            try:
                img_b64 = capture_image()
            except RuntimeError as e:
                return f"Error capturing image: {str(e)}"
        
        if not query or not img_b64:
            return "Error: both 'query' and 'image' are required."
        
        # Initialize Groq client
        client = Groq()
        
        # Prepare messages for the API
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": query
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{img_b64}",
                        },
                    },
                ],
            }
        ]
        
        # Make API call to Groq
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="meta-llama/llama-4-maverick-17b-128e-instruct"  # Updated to a vision model that works with Groq
        )
        
        return chat_completion.choices[0].message.content
        
    except Exception as e:
        print(f"Error in analyze_image_with_query: {str(e)}")
        return f"Error analyzing image: {str(e)}"

# Test function - uncomment to test
# if __name__ == "__main__":
#     query = "what is in the hand of the guy?"
#     print(analyze_image_with_query(query))