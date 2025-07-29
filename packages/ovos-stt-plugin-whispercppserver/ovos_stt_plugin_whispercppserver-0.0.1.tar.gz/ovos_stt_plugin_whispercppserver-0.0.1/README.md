# WHISPER SERVICE OVOS STT CLIENT

OpenVoiceOS plugin for Whisper service, compatible with free Whisper.cpp server

My motivation was to establish a one working STT system for whole
household, additionally to Home Assistant I use it for
[Blurt](https://github.com/QuantiusBenignus/blurt#network-transcription)
gnome shell extension.

You need a running Whisper compatible API service,
for example Whisper.cpp instance:

<https://github.com/ggerganov/whisper.cpp/tree/master/examples/server>

I run it on nvidia GPU with fantastic results with detailed
inference on large model in usually about a second:

```sh
whisper.cpp/server -m whisper.cpp/models/ggml-large-v3-q5_0.bin --host 0.0.0.0 --port 8910 --print-realtime --print-progress
```

You can study whisper.cpp to get more information about running its STT service.

## Install

```sh
pip install ovos-stt-plugin-whispercppserver
```

## Configuration

`~/.config/mycroft/mycroft.conf`

```json
{
  "stt": {
    "module": "ovos-stt-plugin-whispercppserver",
    "ovos-stt-plugin-whispercppserver": {
      "server": "http://192.168.41.49:8910/inference"
      "temperature": "0.0"
      "temperature_inc": "0.2"
      "timeout": 120
    }
  }
}
```

`server`: MANDATORY! your whisper.cpp inference path instance URI

`temperature`: Decoding temperature (default: 0.0)

`temperature_inc`: Temperature increment (default: 0.2)

`timeout`: timeout of inference request (default: 120 seconds)
