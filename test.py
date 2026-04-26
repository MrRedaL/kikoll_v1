import requests
from bs4 import BeautifulSoup
import time
import json
import os

# Remplacez par votre token et chat ID valides
TOKEN = "8639463749:AAFEIwxwzyQm-n98I3D9kqeSTCRwSri1jB4"
CHAT_ID = "6273324705"
HISTORY_FILE = "history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        # On garde les 100 derniers pour éviter que le fichier ne grossisse trop
        json.dump(history[-100:], f, indent=4)

def get_latest_news():
    url = "https://www.welovebuzz.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        news_list = []
        
        # Sur WeLoveBuzz, les titres sont souvent dans des balises h2, h3 avec un lien <a>
        for tag_name in ['h2', 'h3']:
            articles = soup.find_all(tag_name)
            for article in articles:
                a_tag = article.find('a')
                if a_tag and a_tag.get('href') and "welovebuzz.com" in a_tag['href']:
                    title = a_tag.text.strip()
                    link = a_tag['href']
                    
                    # On évite les doublons et les liens vides
                    if title and link not in [n['link'] for n in news_list]:
                        news_list.append({'title': title, 'link': link})
                        
            if news_list: # Si on a trouvé des articles, on arrête de chercher avec d'autres balises
                break
                
        return news_list[:10] # On limite aux 10 premières actualités pour vérifier
    except Exception as e:
        print(f"Erreur lors de la récupération des news: {e}")
        return []

def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        response = requests.post(url, data=payload)
        # Si la requête n'est pas un succès, on affiche l'erreur
        if response.status_code != 200:
            print(f"[ERREUR] {response.status_code}: {response.text}")
        else:
            print("[SUCCES] Message envoyé avec succès !")
    except requests.exceptions.RequestException as e:
        print(f"[ERREUR] de connexion: {e}")

def main():
    print("Recherche des dernières nouvelles sur WeLoveBuzz...")
    news = get_latest_news()
    
    if not news:
        print("Aucune actualité trouvée ou le site a bloqué la requête.")
        return

    history = load_history()
    new_articles = [item for item in news if item['link'] not in history]

    print(f"{len(news)} actualités trouvées. {len(new_articles)} sont nouvelles.")
    
    if not new_articles:
        print("Aucune nouvelle actualité à envoyer.")
        return

    print("Envoi sur Telegram...")
    for item in reversed(new_articles): # On envoie la plus ancienne des nouvelles d'abord
        message = f"📰 <b>{item['title']}</b>\n\n🔗 {item['link']}"
        send_to_telegram(message)
        history.append(item['link'])
        time.sleep(1.5) # Pause pour éviter le spam

    save_history(history)

if __name__ == "__main__":
    main()
