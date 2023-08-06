from speechkit import Session, RecognitionLongAudio
from speechkit.auth import generate_jwt
import time
import os
import json
import subprocess
from datetime import datetime
from dotenv import load_dotenv


load_dotenv()
bucket_name = os.getenv("YANDEX_BUCKET_NAME")
service_account_id = os.getenv("YANDEX_SERVICE_ACC_ID")
key_id = os.getenv("YANDEX_KEY_ID")
private_key = os.getenv("YANDEX_PRIVATE_KEY").replace('\\n', '\n').encode()

class STT:
    default_init = {
        "sample_rate": 16000,
    }

    def __init__(self,
                 sample_rate=None,
                 ) -> None:
        self.sample_rate = sample_rate if sample_rate else STT.default_init["sample_rate"]


    def audio_to_text(self, audio_file_name=None) -> str:
        jwt = generate_jwt(service_account_id, key_id, private_key)
        session = Session.from_jwt(jwt)
        recognize_long_audio = RecognitionLongAudio(session, service_account_id, bucket_name)

        f = open("voice_cache/" + os.path.basename(audio_file_name) + "processing.wav", "w")
        process = subprocess.Popen(
            ["ffmpeg",
             "-loglevel", "quiet",
             "-i", audio_file_name,
             "-ar", str(self.sample_rate),
             "-ac", "1",
             "-acodec", "pcm_s16le",
             "-f", "wav",
             "-"
             ],
            stdout=f
        )

        f.close()
        process.wait()
        recognize_long_audio.send_for_recognition(
            "voice_cache/" + os.path.basename(audio_file_name) + "processing.wav", audioEncoding='LINEAR16_PCM', sampleRateHertz='16000',
            audioChannelCount=1, rawResults=False, profanityFilter='false', literatureText='true',
        )
        try:
            os.remove("voice_cache/" + os.path.basename(audio_file_name) + "processing.wav")
        except:
            pass
        while True:
            time.sleep(2)
            if recognize_long_audio.get_recognition_results():
                break

        data = recognize_long_audio.get_data()
        text = recognize_long_audio.get_raw_text()
        result = text[0]
        for letter in text[1:]:
            if letter.isupper():
                result += f' {letter}'
            else:
                result += letter
        return result
