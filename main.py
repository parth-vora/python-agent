# initialization
# Part 1 - State Tracker

class Agent: 
    def __init__(self):
        # stores past messages (user / msg)
        self.history=[]
        # stores tool name before running it in case it fails
        self.pending_tool= None
        # stores where use is in workflow to track progress
        self.status = "START"

# Part 2 - Routing 

    def llm_router(user_message: str):

        msg = user_message.lower()
        if "refund" in msg or "dispute" in msg:
            return {
                "tool_name": "process_refund",
                "args": {"amount": 15.00, "tx_id": "123"}
            }

        # fallback in case agent doesnt know what to do
        return {
            "tool_name": "transfer_to_human",
            "args": {"reason": "Unknown action"}
        }

# Part 3 - Execution
    def execute(tool_name: str, args: dict) -> str:

        if tool_name == "process_refund":
            amount = args.get("amount",0)

            if amount > 20.00:
                return "Denied, over auto-refund threshold. "

            try: 
                return f"Success, Refunded ${amount} succesfully."
            except Exception as e:
                return f"Failed, System timehout. Retrying later."

        if tool_name == "transfer_to_human":
            return "Success, Transferring to live agent!"


state = Agent()

user_input = "I want a refund for 123"
state.history.append({"role":"user", "content":"user_input"})

tool = state.llm_router(user_input)
state.pending_tool = tool

result = state.execute(tool["tool_name"],tool["args"])
print(result)

        
