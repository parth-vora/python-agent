import os
from google import genai
from google.genai import types

client = genai.Client()

def process_refund(transaction_id: str, amount: float) -> str:
    if amount > 20.00:
        return "Blocked. Higher than approval threshold"

    try:
        receipt = f"key_{transaction_id}"
        return "Success! Refund for {transaction_id} was processed for an amount of ${amount}"
    except Exception as e:
        return "Internal issue, try again later."

def run_agent(user_message:str) -> str:
    config = types.GenerateContentConfig(
        system_instruction = """You are an agent for a retail company. Your task is process refunds and disputes. 
        When you interact with users, you must: 
        1) Be consise. 
        2) If a customer is requesting a refund, use the "process_refund" tool
        3_Extract the transaction id from the user message and exact amount of money in dollars.
        """,
        tools=[process_refund],
        temperature = 0.0
    ) 

    response = client.models.generate_content(
        model = "gemini-2.5-flash",
        contents = user_message,
        config = config
    )

    if response.function_calls:
        for call in response.function_calls:
            function_name = call.name
            function_args = call.args

            if function_name =="process_refund":
                tx_id = function_args.get("transaction_id")
                amt = float(function_args.get("amount",0.0))
                result = process_refund(tx_id, amt)
                return result 
            else:
                return response.text

if __name__ == "__main__":
    print(run_agent("hey i need a refund of 13.50 for my order tx123"))
    print(run_agent("hey i need a refund of 24.50 for my order tx423"))  

