import json

from django.http import JsonResponse
from django.shortcuts import render


def chat_view(request):
    """Renders the chat interface."""
    return render(request, "agents/chat.html")


def chat_api(request):
    """Simple echo/mock API for the agent."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            message = data.get("message", "")

            # TODO: Integrate real LLM here
            response_text = f"I received your message: '{message}'. This is a mock response from the Django Agent."

            return JsonResponse({"response": response_text})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "POST required"}, status=405)
