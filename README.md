# MTS_AI_API_DJANGO
 API, которое может принимать POST-запросы на /synthesize со следующим JSON-телом
Описание API:

Это API предоставляет возможность синтезировать речь на основе текста, используя сервис TTS (Text-to-Speech). Пользователь может отправить POST-запрос на /synthesize, предоставив текст для синтеза речи. В ответ API возвращает синтезированное аудио в формате WAV.

Endpoint:
Copy
POST /synthesize
Параметры запроса:
text (обязательный): Текст, на основе которого будет синтезирована речь.
Пример запроса:
json
Copy
POST /synthesize
Content-Type: application/json

{
  "text": "Привет! Как дела?"
}
Пример ответа:
json
Copy
HTTP/1.1 200 OK
Content-Type: application/json

{
  "audio": "<base64-encoded-audio-data>"
}
Ошибки:
Если запрос не соответствует ожидаемому формату или отсутствует обязательный параметр text, API вернет ошибку с соответствующим статусом и сообщением об ошибке.

json
Copy
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "error": "Invalid request"
}
