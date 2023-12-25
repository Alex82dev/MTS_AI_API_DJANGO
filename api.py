from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os
import random
import grpc
from dotenv import load_dotenv
from keycloak import KeycloakOpenID
from typing import Mapping
import tts_pb2
import tts_pb2_grpc

load_dotenv()

API_ADDRESS = os.environ["API_ADDRESS"]
AUTH_CONFIG = {
    "sso_server_url": os.environ["SSO_SERVER_URL"],
    "realm_name": os.environ["REALM_NAME"],
    "client_id": os.environ["CLIENT_ID"],
    "client_secret": os.environ["CLIENT_SECRET"],
}

@csrf_exempt
def synthesize(request):
    if request.method == "POST":
        data = request.POST
        text = data.get("text")

        if text:
            audio_data = synthesize_speech(text, API_ADDRESS, AUTH_CONFIG)
            return JsonResponse({"audio": audio_data.decode("utf-8")})

    return JsonResponse({"error": "Invalid request"})

def synthesize_speech(text: str, api_address: str, auth_config: Mapping[str, str]):
    request = tts_pb2.SynthesizeSpeechRequest(
        text=text,
        encoding=tts_pb2.AudioEncoding.LINEAR_PCM,
        sample_rate_hertz=22050,
        voice_name="gandzhaev",
        synthesize_options=tts_pb2.SynthesizeOptions(
            postprocessing_mode=tts_pb2.SynthesizeOptions.PostprocessingMode.POST_PROCESSING_DISABLE,
            model_type="default",
            voice_style=tts_pb2.VoiceStyle.VOICE_STYLE_NEUTRAL,
        ),
    )

    options = [
        ("grpc.min_reconnect_backoff_ms", 1000),
        ("grpc.max_reconnect_backoff_ms", 1000),
        ("grpc.max_send_message_length", -1),
        ("grpc.max_receive_message_length", -1),
    ]

    credentials = grpc.ssl_channel_credentials()

    with grpc.secure_channel(
        api_address, credentials=credentials, options=options
    ) as channel:
        stub = tts_pb2_grpc.TTSStub(channel)

        request_metadata = get_request_metadata(auth_config)

        response, call = stub.Synthesize.with_call(
            request,
            metadata=request_metadata,
            wait_for_ready=True,
        )

    path = "synthesized_audio.wav"
    with open(path, "wb") as f:
        f.write(response.audio)

    with open(path, "rb") as f:
        audio_data = f.read()

    return audio_data

def get_request_metadata(auth_config: Mapping[str, str]) -> list[tuple[str, str]]:
    sso_connection = KeycloakOpenID(
        auth_config["sso_server_url"],
        auth_config["realm_name"],
        auth_config["client_id"],
        auth_config["client_secret"],
        verify=True,
    )
    token_info = sso_connection.token(grant_type="client_credentials")
    access_token = token_info["access_token"]

    trace_id = str(random.randint(1000, 9999))
    print(f"Trace id: {trace_id}")

    metadata = [
        ("authorization", f"Bearer {access_token}"),
        ("external_trace_id", trace_id),
    ]

    return metadata
