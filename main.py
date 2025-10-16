import speech_recognition as sr
import os
import webbrowser
import datetime
from dotenv import load_dotenv
import google.generativeai as genai

# ------------------- Gemini API -------------------
# Load environment variables from .env
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)
gemini_model = genai.GenerativeModel("models/gemini-2.5-flash")

# ------------------- Session Memory -------------------
memory = {
    "last_search": [],      # store URLs of last search
    "last_song": None,      # store last played song name
    "last_site": None,      # store last opened site URL
    "last_command": None    # track type of last command
}

# ------------------- Helper Functions -------------------
def say(text):
    os.system(f'say "{text}" -v Alex')

def query_gemini(prompt):
    try:
        response = gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"[Gemini API Error] {e}")
        return "Sorry, I could not process that."

def hear():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=1)
        print("Listening...")
        audio = r.listen(source)
        try:
            print("Recognizing...")
            query = r.recognize_google(audio, language="en-in")
            print(f"User said: {query}")
            return query.lower().strip()
        except Exception:
            return ""

# ------------------- Main Loop -------------------
if __name__ == "__main__":
    print("pycharm")
    say("Greetings Mr. Rath, Vision here ready to serve you.")

    # Predefined songs and sites
    songs = [
        ["mockingbird", "https://open.spotify.com/track/561jH07mF1jHuk7KlaeF0s"],
        ["sunflower", "https://open.spotify.com/track/3KkXRkHbMCARz0aVfEt68P"],
        ["we will rock you", "https://open.spotify.com/track/4pbJqGIASGPr0ZpGpnWkDn"],
        ["winning speech", "https://open.spotify.com/track/3FqtduiaqnFYvBgKuc6QWQ"]
    ]

    sites = [
        ["youtube", "https://www.youtube.com"],
        ["google", "https://www.google.com"],
        ["instagram", "https://www.instagram.com"]
    ]

    while True:
        exit_keywords = ["exit", "quit", "stop"]
        query = hear()

        if not query:
            continue  # skip if nothing recognized

        # Exit commands
        if any(word in query for word in exit_keywords):
            say("Goodbye, Mr. Rath!")
            print("Goodbye, Mr. Rath!")
            break

        handled = False

        # ------------------- Site Opening -------------------
        for site in sites:
            if f"open {site[0]}" in query:
                say(f"Yes Mr. Rath, opening {site[0]}")
                webbrowser.open(site[1])
                # Store in memory
                memory["last_site"] = site[1]
                memory["last_command"] = "site"
                handled = True
                break

        # ------------------- Music -------------------
        if "play music" in query:
            say("Yes Mr. Rath, I have your playlist ready. Which song would you like me to play?")
            songselection = hear()
            found = False
            for song in songs:
                if song[0].lower() in songselection:
                    say(f"Yes Mr. Rath, playing {song[0]} on Spotify now.")
                    webbrowser.open(song[1])
                    # Store in memory
                    memory["last_song"] = song[0]
                    memory["last_command"] = "music"
                    found = True
                    break
            if not found:
                say("Sorry, I couldn't find that song in your playlist. Searching on Spotify...")
                webbrowser.open(f"https://open.spotify.com/search/{songselection}")
            handled = True

        # Play last song
        if "play last song" in query:
            if memory.get("last_song"):
                song_name = memory["last_song"]
                say(f"Playing your last song: {song_name}")
                for song in songs:
                    if song[0].lower() == song_name.lower():
                        webbrowser.open(song[1])
                        break
                handled = True
            else:
                say("No song is stored in memory.")

        # ------------------- Time / Date / Day -------------------
        if "time" in query:
            strftime = datetime.datetime.now().strftime("%H:%M:%S")
            say(f"Mister Rath, the time is {strftime}")
            handled = True
        elif "date" in query:
            today = datetime.datetime.now().strftime("%d-%m-%Y")
            say(f"Mister Rath, today is {today}")
            handled = True
        elif "day" in query:
            day = datetime.datetime.now().strftime("%A")
            say(f"Mister Rath, today is {day}")
            handled = True

        # ------------------- Search Online -------------------
        if "search online" in query:
            search_query = query.replace("search online", "").strip()
            search_url = f"https://www.google.com/search?q={search_query}"
            webbrowser.open(search_url)
            # Store search in memory
            memory["last_search"] = [search_url]
            memory["last_command"] = "search"
            handled = True

        # Open first search link from memory
        if "open the first link" in query or "open first result" in query:
            if memory.get("last_command") == "search" and memory.get("last_search"):
                say("Opening the first result from your last search")
                webbrowser.open(memory["last_search"][0])
                handled = True
            else:
                say("No previous search found.")

        # Open last site
        if "open last site" in query:
            if memory.get("last_command") == "site" and memory.get("last_site"):
                say("Opening your last site again")
                webbrowser.open(memory["last_site"])
                handled = True
            else:
                say("No previous site found.")

        # ------------------- Gemini AI -------------------
        if not handled:
            response_text = query_gemini(query)
            print(f"Vision AI: {response_text}")
            say(response_text)