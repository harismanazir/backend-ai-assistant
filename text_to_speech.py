import os
# import elevenlabs
# from elevenlabs.client import ElevenLabs
import subprocess
import platform
from pydub import AudioSegment

# ELEVENLABS_API_KEY=os.environ.get("ELEVENLABS_API_KEY")


# def text_to_speech_with_elevenlabs(input_text, output_filepath):
#     client=ElevenLabs(api_key=ELEVENLABS_API_KEY)
#     audio=client.text_to_speech.convert(
#         text= input_text,
#         voice_id="ZF6FPAbjXT4488VcRRnw", #"JBFqnCBsd6RMkjVDRZzb",
#         model_id="eleven_multilingual_v2",
#         output_format= "mp3_22050_32",
#     )
#     elevenlabs.save(audio, output_filepath)

#     wav_filepath = "final.wav"
#     audio = AudioSegment.from_mp3(output_filepath)
#     audio.export(wav_filepath, format="wav")
#     os_name = platform.system()
#     try:
#         if os_name == "Darwin":  # macOS
#             subprocess.run(['afplay', output_filepath])
#         elif os_name == "Windows":  # Windows
#             subprocess.run(['powershell', '-c', f'(New-Object Media.SoundPlayer "{wav_filepath}").PlaySync();'])
#         elif os_name == "Linux":  # Linux
#             subprocess.run(['aplay', output_filepath])  # Alternative: use 'mpg123' or 'ffplay'
#         else:
#             raise OSError("Unsupported operating system")
#     except Exception as e:
#         print(f"An error occurred while trying to play the audio: {e}")


from gtts import gTTS

def text_to_speech_with_gtts(input_text, output_filepath="final.mp3", play_locally=False, retries=3):
    """
    Converts text to speech using gTTS, saves as MP3, and returns the file path.
    Works both locally and on Render. Avoids subprocess playback on Render.
    """

    attempt = 0
    while attempt < retries:
        try:
            # Generate the MP3 file
            tts = gTTS(text=input_text, lang="en")
            tts.save(output_filepath)

            # Convert to WAV if needed for browser playback
            wav_filepath = "final.wav"
            sound = AudioSegment.from_mp3(output_filepath)
            sound.export(wav_filepath, format="wav")

            # Optional: Play audio locally only if enabled
            if play_locally:
                os_name = platform.system()
                try:
                    if os_name == "Darwin":  # macOS
                        subprocess.run(['afplay', wav_filepath])
                    elif os_name == "Windows":  # Windows
                        subprocess.run(['powershell', '-c', f'(New-Object Media.SoundPlayer "{wav_filepath}").PlaySync();'])
                    elif os_name == "Linux":  # Linux
                        subprocess.run(['aplay', wav_filepath])
                except Exception as e:
                    print(f"Local audio playback failed: {e}")

            return output_filepath

        except Exception as e:
            # Handle Google Translate API Rate Limit (HTTP 429)
            if "429" in str(e):
                wait_time = random.randint(2, 5)
                print(f"⚠️ gTTS rate limit hit. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                attempt += 1
            else:
                print(f"❌ gTTS failed: {e}")
                break

    # If all retries fail
    return None

# input_text = "Hi, I am Haris, I just wanna say that I love you Rehma"
# output_filepath = "test_text_to_speech.mp3"
# #text_to_speech_with_elevenlabs(input_text, output_filepath)
# text_to_speech_with_gtts(input_text, output_filepath)