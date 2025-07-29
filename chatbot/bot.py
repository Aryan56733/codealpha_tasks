import nltk
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

faq_data = {
    "What is your return policy?": "You can return any product within 30 days of purchase.",
    "How can I track my order?": "You can track your order using the tracking number sent to your email.",
    "What payment methods do you accept?": "We accept credit cards, PayPal, and bank transfers.",
    "Do you offer customer support?": "Yes, 24/7 customer support is available via chat and email.",
    "How long does delivery take?": "Standard delivery usually takes 3-5 business days.",
}


nltk.download('punkt')

questions = list(faq_data.keys())
answers = list(faq_data.values())

# Vectorizer
vectorizer = TfidfVectorizer(tokenizer=nltk.word_tokenize, stop_words='english')
tfidf_matrix = vectorizer.fit_transform(questions)

def get_best_answer(user_question):
    user_vec = vectorizer.transform([user_question])
    similarities = cosine_similarity(user_vec, tfidf_matrix)
    best_idx = np.argmax(similarities)

    if similarities[0][best_idx] > 0.3:  # Confidence threshold
        return answers[best_idx]
    else:
        return "Sorry, I couldn't find a relevant answer. Please try again."

def chatbot():
    print("FAQ Chatbot (type 'exit' to quit)")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit']:
            print("Bot: Goodbye!")
            break
        response = get_best_answer(user_input)
        print(f"Bot: {response}")

if __name__ == "__main__":
    chatbot()
