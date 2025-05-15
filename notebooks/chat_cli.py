#!/usr/bin/env python3
import argparse
from langchain_ollama.chat_models import ChatOllama
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage
import requests

#
#   TOOL DEFINITION
#

@tool
def get_weather(latitude, longitude):
    """Fetches weather for given city"""

    response = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m")
    data = response.json()
    return data['current']['temperature_2m']


#
#   RESPONSE FUNCTION
#

def get_response(prompt: str, use_function_calling: bool):
    messages = [
        SystemMessage("You are a helpful AI assistant. Answer concisely."),
        HumanMessage(prompt)
    ]

    if use_function_calling:
        model = ChatOllama(model="llama3.2").bind_tools([get_weather])
        # initial call
        res = model.invoke(messages)
        messages.append(res)

        # run any tool calls
        for tool_call in res.tool_calls:
            fn = tool_call["name"].lower()
            tool_fn = {"get_weather": get_weather}[fn]
            tool_msg = tool_fn.invoke(tool_call)
            messages.append(tool_msg)

        # final call with tool output
        res = model.invoke(messages)
        messages.append(res)
    else:
        model = ChatOllama(model="llama3.2")
        res = model.invoke(messages)
        messages.append(res)

    return res.content, messages

#
#   MAIN ENTRYPOINT
#

def main():
    parser = argparse.ArgumentParser(description="ChatOllama terminal client")
    parser.add_argument(
        "--prompt", "-p",
        type=str,
        required=True,
        help="The prompt to send to the assistant"
    )
    parser.add_argument(
        "--function-calling", "-f",
        action="store_true",
        help="Enable LangChain function calling (get_weather)"
    )
    args = parser.parse_args()

    response_text, chat_history = get_response(args.prompt, args.function_calling)

    print("\n=== Assistant response ===")
    print(response_text)

    print("\n=== Full chat messages ===")
    for msg in chat_history:
        role = getattr(msg, "role", msg.type)
        content = getattr(msg, "content", str(msg))
        print(f"[{role}] {content}")

if __name__ == "__main__":
    main()
