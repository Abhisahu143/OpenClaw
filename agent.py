import os
import google.generativeai as genai
from dotenv import load_dotenv

from tools import search_web, send_email, AVAILABLE_TOOLS

load_dotenv()

# Configure Google Gemini API Key
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Create a master list of tool descriptions for the LLM
TOOL_DESCRIPTIONS = [
    {
        "name": "search_web",
        "description": "Searches the web using DuckDuckGo and returns top results. Use this tool when the user asks for current events, facts, or information you don't know natively.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to search for on DuckDuckGo.",
                }
            },
            "required": ["query"],
        },
    },
    {
        "name": "send_email",
        "description": "Sends an email to the specified address. Use this tool when the user explicitly asks to send an email.",
        "parameters": {
            "type": "object",
            "properties": {
                "to_email": {
                    "type": "string",
                    "description": "The recipient's email address.",
                },
                "subject": {
                    "type": "string",
                    "description": "The subject of the email.",
                },
                "body": {
                    "type": "string",
                    "description": "The main content text of the email.",
                }
            },
            "required": ["to_email", "subject", "body"],
        },
    },
    {
        "name": "get_current_time",
        "description": "Returns the current date and time. Use this when the user asks for the time or needs relative time awareness.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "extract_website_text",
        "description": "Fetches and returns the text content of a specific URL. Use this when the user provides a link and asks you to summarize, read, or analyze its contents.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The full HTTP/HTTPS URL of the website to read.",
                }
            },
            "required": ["url"],
        },
    }
]

# Initialize the Gemini model for chatting, supplying tools
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    tools=TOOL_DESCRIPTIONS,
    system_instruction=(
        "You are OpenClaw Clone, a highly capable, autonomous, pro-level Agentic AI assistant. "
        "You have access to tools that let you search the live web, read the contents of URLs, "
        "check the current time, and send emails.\n\n"
        "RULES:\n"
        "1. BE PROACTIVE. If a user asks a question, ALWAYS use your tools to find the answer if "
        "you are not 100% certain of the most up-to-date facts.\n"
        "2. If a user gives you a link, use the extract_website_text tool to read it.\n"
        "3. Only ask for permission if an action is destructive or unclear. Otherwise, just do it.\n"
        "4. Your responses should be concise, professional, and directly state what you accomplished."
    )
)


def start_chat_session():
    """Starts a new chat session to maintain conversation context."""
    return model.start_chat()


def handle_message(chat_session, user_prompt: str) -> str:
    """
    Sends a message to the Gemini Agent and handles function calling if requested by the LLM.
    """
    response = chat_session.send_message(user_prompt)
    
    # Check if Gemini decided to call a function/tool
    if response.function_call:
        fn = response.function_call
        fn_name = fn.name
        fn_args = {k: v for k, v in fn.args.items()}
        
        print(f"Agent requested tool: {fn_name} with args: {fn_args}")
        
        # Execute the function
        if fn_name in AVAILABLE_TOOLS:
            try:
                tool_result = AVAILABLE_TOOLS[fn_name](**fn_args)
                
                # Send the function's result back to the model 
                # (so it can read the search results or confirm email sending)
                response = chat_session.send_message(
                    genai.types.Part.from_function_response(
                        name=fn_name,
                        response={"result": tool_result}
                    )
                )
            except Exception as e:
                response = chat_session.send_message(
                    genai.types.Part.from_function_response(
                        name=fn_name,
                        response={"error": str(e)}
                    )
                )

    # Return the final text string output from the LLM
    return response.text
