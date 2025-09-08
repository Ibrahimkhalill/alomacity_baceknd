import os
import logging
from openai import OpenAI
from dotenv import load_dotenv
 
# Load environment variables from .env file
load_dotenv()
 
OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY   # use your own API key
if not os.getenv("OPENAI_API_KEY"):
    print("Error: OPENAI_API_KEY environment variable not set.")
    exit()
 
client = OpenAI() # Will now use OPENAI_API_KEY from .env file
 
# Configure basic logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
 
# --- Helper Function for OpenAI API Call ---
def get_openai_sentiment(text_content: str, model: str = "gpt-4o-mini", temperature: float = 0.1) -> str:
    """
    Calls the OpenAI API to get sentiment for the given text.
 
    Args:
        text_content (str): The text to analyze.
        model (str): The OpenAI model to use.
        temperature (float): The sampling temperature for the model.
 
    Returns:
        str: "positive", "negative", or "neutral" (as a fallback if parsing fails).
    """
    if not text_content or text_content.isspace():
        logging.warning("Received empty text_content for sentiment analysis.")
        return "neutral" # Cannot determine sentiment for empty text
 
    system_prompt = (
        "You are a sentiment analysis expert. Your task is to classify the sentiment "
        "of the provided news article content as either 'positive' or 'negative'. "
        "Consider the overall emotional tone and impact of the news. "
        "Respond with ONLY the word 'positive' or 'negative'."
    )
 
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text_content}
            ],
            temperature=temperature,
            max_tokens=10  # "positive" or "negative" is short
        )
        sentiment = completion.choices[0].message.content.strip().lower()
 
        if sentiment in ["positive", "negative"]:
            return sentiment
        else:
            # This case handles if the model returns something unexpected
            logging.warning(f"OpenAI returned an unexpected sentiment: '{sentiment}'. Input: '{text_content[:100]}...'")
           
            if "positive" in sentiment: return "positive" # Basic guard
            if "negative" in sentiment: return "negative" # Basic guard
            return "neutral" # Fallback if not strictly "positive" or "negative"
 
    except Exception as e:
        logging.error(f"Error calling OpenAI API for sentiment: {e}")
        return None # Indicates an API call or processing error
 
# --- Main Sentiment Analysis Function ---
def analyze_news_item_sentiment(news_data: dict) -> str:
    """
    Analyzes the sentiment of a news item based on its fields.
 
    Args:
        news_data (dict): A dictionary containing news item fields:
            'Category' (str, optional)
            'URL' (str, optional but good for logging)
            'Headline' (str)
            'Image' (str, optional)
            'Description' (str, optional)
            'Published Datetime' (str, optional)
            'Published Text' (str, optional) - This field from your example seems to be
                                            just a formatted datetime, not the article body.
                                            If it *were* the full article text, it would be primary.
 
    Returns:
        str: The predicted sentiment ("positive", "negative", "neutral" or "error").
    """
    if not isinstance(news_data, dict):
        logging.error("Invalid input: news_data must be a dictionary.")
        return None
 
    headline = news_data.get("Headline", "")
    description = news_data.get("Description", "")
   
    text_for_analysis = []
    if headline:
        text_for_analysis.append(f"Headline: {headline}")
    if description:
        # Limit description length if it's extremely long to manage token usage
        # For GPT-3.5-turbo, context window is ~4k tokens, GPT-4 ~8k or ~32k.
        # A typical word is ~1.3 tokens.
        max_desc_chars = 3000 # Approx 750 words / 1000 tokens, adjustable
        truncated_description = description[:max_desc_chars]
        if len(description) > max_desc_chars:
            truncated_description += "..."
        text_for_analysis.append(f"Description: {truncated_description}")
 
    if not text_for_analysis:
        logging.warning(f"No text content (headline/description) found for sentiment analysis. URL: {news_data.get('URL', 'N/A')}")
        return "neutral" # Or "error" depending on how you want to handle this
 
    combined_text = "\n\n".join(text_for_analysis)
 
    logging.info(f"Analyzing sentiment for URL: {news_data.get('URL', 'N/A')}")
    sentiment = get_openai_sentiment(combined_text)
    print("Predicted sentiment", sentiment)
    logging.info(f"Predicted sentiment: {sentiment} for URL: {news_data.get('URL', 'N/A')}")
 
    return sentiment