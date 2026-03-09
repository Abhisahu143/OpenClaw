import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from dotenv import load_dotenv

load_dotenv()

def search_web(query: str) -> str:
    """
    Searches the web using DuckDuckGo and returns the top results as a string.
    Use this tool when the user asks for current events, facts, or information you don't know natively.
    """
    try:
        results = DDGS().text(query, max_results=3)
        if not results:
            return "No results found."
        
        formatted_results = []
        for r in results:
            formatted_results.append(f"Title: {r['title']}\nSummary: {r['body']}\nURL: {r['href']}\n")
            
        return "\n".join(formatted_results)
    except Exception as e:
        return f"Error performing search: {str(e)}"

def send_email(to_email: str, subject: str, body: str) -> str:
    """
    Sends an email to the specified address.
    Use this tool when the user explicitly asks to send an email.
    """
    # Requires EMAIL_USER and EMAIL_PASS set in environment variables
    from_email = os.environ.get("EMAIL_USER")
    password = os.environ.get("EMAIL_PASS")
    
    if not from_email or not password:
        return "Error: Email credentials are not configured on the server."
        
    try:
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Using Gmail SMTP server. Change if using a different provider.
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, password)
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        
        return f"Email successfully sent to {to_email}."
    except Exception as e:
        return f"Failed to send email: {str(e)}"

def get_current_time() -> str:
    """Returns the current date and time."""
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

def extract_website_text(url: str) -> str:
    """Fetches text content from a given URL."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
        text = soup.get_text(separator=' ', strip=True)
        # return only first 3000 chars to avoid overwhelming LLM token limits
        return text[:3000] + ("..." if len(text) > 3000 else "")
    except Exception as e:
        return f"Error reading URL: {str(e)}"

# A dictionary mapping tool names to actual functions, useful for the Agent
AVAILABLE_TOOLS = {
    "search_web": search_web,
    "send_email": send_email,
    "get_current_time": get_current_time,
    "extract_website_text": extract_website_text,
}
