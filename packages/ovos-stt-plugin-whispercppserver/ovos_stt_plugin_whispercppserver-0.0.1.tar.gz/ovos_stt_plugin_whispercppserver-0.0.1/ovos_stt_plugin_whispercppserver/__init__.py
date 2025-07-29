
# for a very deep development turn on logging 
#import logging
#logging.basicConfig(level=logging.DEBUG)

import httpx
import wave

from io import BytesIO
from ovos_config import Configuration
from ovos_plugin_manager.stt import STT
from ovos_utils import classproperty
from ovos_utils.log import LOG
from tempfile import NamedTemporaryFile

class OVOSWCPPSSTT(STT):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        config = Configuration().get("stt", {}).get("ovos-stt-plugin-whispercppserver", {})
        LOG.debug(config)
        self.temperature = config.get("temperature", "0.0")
        self.temperature_inc = config.get("temperature_inc", "0.2")
        self.timeout = config.get("timeout", 120)
        self.server = config.get("server")

    def execute(self, audio, language="auto"):
        lang = language or self.lang
        url = f"{self.server}"
        params = {
            "temperature": self.temperature,
            "temperature_inc": self.temperature_inc,
            "language": lang,
        }
        with BytesIO() as tmpfile:
            with wave.open(tmpfile, 'wb') as wavfile:
                wavfile.setparams((1, 2, 16000, 0, 'NONE', 'NONE'))
                wavfile.writeframes(audio.get_wav_data())

                files = {"file": tmpfile.getvalue()}

                with httpx.Client() as client:
                    response = client.post(
                        url,
                        files=files,
                        params=params,
                        timeout=self.timeout)
                    LOG.debug(f"{response.status_code}:{response.text}")
                    return response.json()['text']

    @classproperty
    def available_languages(self) -> set:
        """Return languages supported by this TTS implementation in this state
        This property should be overridden by the derived class to advertise
        what languages that engine supports.
        Returns:
            set: supported languages
        """
        return set()  # TODO
