import json
import os
import requests
from openai import OpenAI

#intialize client
client = OpenAI()

# Part 1 - Define prompt and tools

SYSTEM_PROMPT = """
You are an agent for a retail company. Your task is process refunds and disputes. 
When you interact with users, you must: 
1) Be consise. 
2) If a customer is requesting a refund, use the "process_refund" tool
3_Extract the transaction id from the user message and exact amount of money in dollars.
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "process_refund",
            "description": "API call to reverse charges and issue refunds",
            "parameters": {
                "type": "object",
                "properties": {
                    "transaction_id": {"type":"string", "transaction": "the transactionID starting with tx"},
                    "amount": {"type":"number", "description": "dollar amount of refund"}
                },
                "required": ["transaction_id", "amount"]
            }
        }
    }
]

# Part 2 - The API Calls

def process_refund(transaction_id:str, amount:float) -> str:
    if amount > 20.00:
        return "BLOCKED, cannot be auto approved"

    try: 
        payload = {"tx_id":transaction_id, "refund_value":amount, "key":f"key_{transaction_id}"}
        return "Success. Refund for ${amount} was processed for {transaction_id}."
    except requests.exceptions.Timeout:
        return "Error, timeout - try again later. "
    except Exception as e:
        return "Processing error, try again later."

# Part 3 - Execution Loop

def run_agent(user_message: str):
    msg = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message}
    ]

    response = client.chat.completions.create(
        model = "gpt-4o",
        messages = msg,
        tools = TOOLS,
        tool_choice = "auto"
    )

    ai_response = response.choices[0].message

    if ai_response:
        print("AI responded and triggered a tool call")

    for tool_call in ai_response.tool_calls:
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)

        if function_name == "process_refund":
            api_result = process_refund(
                transaction_id=function_args.get("transaction_id"),
                amonut = float(function_args.get("amount",0))
            )
            return api_result

        else: 
            print(f"LLM Response: {ai_response.content}")
            return ai_response.content

if __name__ == "__main__":
    run_agent("Hey, I never received my order tx_999. Can I please get my $14.50 back?")
    run_agent("I want a refund of $150.00 for fraud on my account tx_777.")
    
