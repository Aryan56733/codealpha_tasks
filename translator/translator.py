import tkinter as tk
from tkinter import ttk, messagebox
import requests, uuid
from dotenv import load_dotenv
import os


load_dotenv()

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY")
region = os.getenv("AZURE_REGION")
endpoint = os.getenv("AZURE_ENDPOINT")


def translate_text():
    text = input_text.get("1.0", tk.END).strip()
    to_lang = lang_var.get()

    if not text:
        messagebox.showwarning("Input Error", "Please enter text to translate.")
        return

    try:
        path = '/translate?api-version=3.0'
        params = f'&to={to_lang}'
        url = endpoint + path + params

        headers = {
            'Ocp-Apim-Subscription-Key': subscription_key,
            'Ocp-Apim-Subscription-Region': region,
            'Content-type': 'application/json',
            'X-ClientTraceId': str(uuid.uuid4())
        }

        body = [{'text': text}]
        response = requests.post(url, headers=headers, json=body)
        result = response.json()

        translated = result[0]['translations'][0]['text']
        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, translated)

    except Exception as e:
        messagebox.showerror("Error", f"Translation failed.\n{e}")

# Teh GUI setup
root = tk.Tk()
root.title("Language Translator")
root.geometry("500x400")


languages = {
    "French": "fr",
    "Spanish": "es",
    "German": "de",
    "Chinese (Simplified)": "zh-Hans",
    "Japanese": "ja",
    "Hindi": "hi"
}
lang_var = tk.StringVar(value="fr")

ttk.Label(root, text="Translate to:").pack(pady=5)
ttk.OptionMenu(root, lang_var, "fr", *languages.values()).pack()

# Input 
ttk.Label(root, text="Enter text:").pack(pady=5)
input_text = tk.Text(root, height=6, width=50)
input_text.pack()

# Translate button
ttk.Button(root, text="Translate", command=translate_text).pack(pady=10)

# Output
ttk.Label(root, text="Translated text:").pack(pady=5)
output_text = tk.Text(root, height=6, width=50)
output_text.pack()

root.mainloop()
