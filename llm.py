import logging
from config import settings

from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

logger = logging.getLogger(__name__)

llm = ChatOllama(model=settings.LLM_MODEL, format="json", temperature=0)
prompt = PromptTemplate(
    template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|> You are a sentiment analysis assessing whether the finance news headlines 
    offer a 'positive', 'negative', or 'neutral' sentiment. You are only to evaluate the sentiment with those one word options and also provide a probability
    decimal value between 0 and 1 where 0 represents a blind guess and 1 represents absolute certainty. Keep your probability values to 3 decimal places. 
    Provide the sentiment and probability as a JSON with the key 'sentiment' for the sentiment and 'probability' for the probability. Do not include a preamble or explanation.
     <|eot_id|><|start_header_id|>user<|end_header_id|> Here are the news headlines:
    \n ------- \n
    {news_headlines} 
    \n ------- \n
    <|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
    input_variables=["news_headlines"],
)


def estimate_sentiment(news_headlines, llm=llm, prompt=prompt):
    """
    Generates sentiment analysis based on given news headlines.
    Returns "positive", "negative", or "neutral" corresponding to the sentiment
    and a decimal value between 0 to 1 on the probability of the generated sentiment
    where 0 represents a complete guess and 1 represents absolute certaintiy.
    """
    sentiment_analyzer = prompt | llm | JsonOutputParser()
    analysis = sentiment_analyzer.invoke({"news_headlines": news_headlines})
    logger.debug(analysis)
    return analysis


if __name__ == "__main__":
    neg_news_headlines = [
        "Tesla stock to drop due to failing batteries!",
        "Elon Musk steps down as CEO, appoints dog in his stead.",
    ]
    analysis = estimate_sentiment(neg_news_headlines)
    print(f"Expected Negative Sentiment -- Analysis: {analysis}")

    pos_news_headlines = [
        "Tesla enters a new era of booming electric vehicles!",
        "Tesla EV sales expected to grow due to high demand!",
    ]
    analysis = estimate_sentiment(pos_news_headlines)
    print(f"Expected Positive Sentiment -- Analysis: {analysis}")

    neu_news_headlines = [
        "Could Tesla possibly make a comeback?",
        "The future of Elon Musk's company is unsure.",
    ]
    analysis = estimate_sentiment(neu_news_headlines)
    print(f"Expected Neutral Sentiment -- Analysis: {analysis}")
