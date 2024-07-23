import random
import re
import json
from collections import deque

class SecureRoadmanAI:
    def __init__(self):
        self.name = "Roadie"
        self.greetings = [f"Yo, what's good? I'm {self.name}, you get me?", "Wagwan fam?", "Sup blud?", "Oi oi, you got me?"]
        self.farewells = [f"I'm gonna bounce, yeah? Catch you later from {self.name}.", "Laters, fam.", "Stay safe, bruv.", f"I'm out, you get me? - {self.name}"]
        self.knowledge_base = self.load_knowledge_base()
        self.conversation_history = {}
        self.user_learned_info = {}
        self.load_learned_info()
        self.banned_words = set()  # Initialize with actual banned words if needed

    def load_knowledge_base(self):
        try:
            with open('knowledge_base.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("Knowledge base file not found. Creating a new one.")
            return {}

    def save_knowledge_base(self):
        with open('knowledge_base.json', 'w') as f:
            json.dump(self.knowledge_base, f, indent=2)

    def load_learned_info(self):
        try:
            with open('learned_info.json', 'r') as f:
                content = f.read().strip()
                if content:
                    self.user_learned_info = json.loads(content)
                else:
                    self.user_learned_info = {}
        except FileNotFoundError:
            self.user_learned_info = {}

    def save_learned_info(self):
        with open('learned_info.json', 'w') as f:
            json.dump(self.user_learned_info, f, indent=2)

    def greet(self, name):
        greeting = random.choice(self.greetings)
        return f"{greeting} Nice to meet you, {name}!"

    def farewell(self):
        return random.choice(self.farewells)

    def roadmanify(self, response):
        roadman_translations = {
            "I": "Man",
            "My": "Man's",
            "Me": "Man",
            "Am": "Is",
            "Are": "Are",  # Keep this as "Are"
            "Hello": "Yo",
            "Hi": "Sup",
            "Yes": "Yeah fam",
            "No": "Nah bruv",
            "Thank you": "Safe one",
            "Thanks": "Bless",
            "Please": "Yo",
            "Okay": "Aight",
            "Cool": "Peak",
        }
        
        # New logic to handle pluralization
        if "is" in response and any(word in response.lower() for word in ["dogs", "cats", "birds", "fish", "reptiles", "amphibians", "mammals", "insects", "spiders", "crustaceans", "mollusks", "worms"]):
            response = response.replace("is", "are")

        for standard, roadman in roadman_translations.items():
            response = re.sub(r'\b' + standard + r'\b', roadman, response, flags=re.IGNORECASE)
        
        response += random.choice([" You get me?", " Innit.", " Safe.", ""])
        return response

    def sanitize_input(self, user_input):
        sanitized = re.sub(r'[^\w\s?.,!]', '', user_input)
        if any(word in sanitized.lower().split() for word in self.banned_words):
            return None
        return sanitized

    def respond(self, user_input, name):
        sanitized_input = self.sanitize_input(user_input)
        if sanitized_input is None:
            return "Oi, watch your language, fam. Keep it clean, yeah?"

        sanitized_input = sanitized_input.lower()
        self.update_conversation_history(name, sanitized_input)

        # Handle basic greetings
        greetings = ["hello", "hi", "hey", "yo", "sup", "what's up", "how are you", "how's it going"]
        if any(greeting in sanitized_input for greeting in greetings):
            return self.get_greeting_response(name)

        # Handle name-related questions
        if "what's my name" in sanitized_input or "what is my name" in sanitized_input:
            return f"Your name is {name}, innit? Man's got a good memory, you get me?"

        if "what's your name" in sanitized_input or "what is your name" in sanitized_input:
            return f"Fam, they call me {self.name}, you get me?"

        if "your name" in sanitized_input:
            return f"Fam, they call me {self.name}, you get me?"

        # Handle goodbyes
        goodbyes = ["bye", "goodbye", "see you", "see you later", "close chat", "exit", "quit"]
        if any(goodbye in sanitized_input for goodbye in goodbyes):
            return "farewell"

        # Check for learned responses
        learned_response = self.check_learned_responses(sanitized_input, name)
        if learned_response:
            return learned_response

        # Check for general responses
        for category in self.knowledge_base:
            for key, value in self.knowledge_base[category].items():
                if key in sanitized_input:
                    return self.roadmanify(value)

        # Context-based responses for vague inputs
        context_response = self.get_context_response(sanitized_input)
        if context_response:
            return context_response

        # Try to learn from the input
        learning_response = self.try_learn_from_input(sanitized_input, name)
        if learning_response:
            return learning_response

        return self.get_fallback_response(sanitized_input)

    def update_conversation_history(self, name, user_input):
        if name not in self.conversation_history:
            self.conversation_history[name] = deque(maxlen=5)
        self.conversation_history[name].append(user_input)

    def check_learned_responses(self, user_input, name):
        if name in self.user_learned_info:
            for pattern, response in self.user_learned_info[name].items():
                if pattern in user_input:
                    return self.roadmanify(response)
        return None

    def get_context_response(self, user_input):
        if any(word in user_input for word in ["not much", "not doing much", "just chilling", "same old", "not really"]):
            return "Sounds chill, fam! Anything specific you wanna chat about?"
        if "hmm" in user_input:
            return "You seem deep in thought, bruv. What's on your mind?"
        
        positive_words = ["good", "great", "excellent", "amazing", "wonderful", "fantastic"]
        negative_words = ["bad", "terrible", "awful", "horrible", "disappointing"]
        
        if any(word in user_input for word in positive_words):
            return "That's peng, fam! What else you wanna chat about?"
        elif any(word in user_input for word in negative_words):
            return "That's bare peak, bruv. Wanna chat it out?"
        
        return None

    def try_learn_from_input(self, user_input, name):
        patterns = [
            r"(.+) (is|are) (.+)",
            r"(.+) (has|have) (.+)",
            r"(.+) (can|could|will|would) (.+)",
        ]
        for pattern in patterns:
            match = re.match(pattern, user_input)
            if match:
                subject = match.group(1)
                verb = match.group(2)
                definition = match.group(3)
                learned_response = f"{subject.capitalize()} {verb} {definition}"
                if self.learn(subject, learned_response, name):
                    category = self.categorize_learned_info(subject)
                    self.knowledge_base[category][subject.lower()] = self.roadmanify(learned_response)
                    self.save_knowledge_base()
                    return f"Safe for the knowledge about {subject}, fam. Man's added that to the brain, you get me?"
                else:
                    return "Nah fam, can't learn that. Keep it clean, yeah?"

        question_match = re.match(r"what (is|are) (.+)\?", user_input)
        if question_match and question_match.group(2) not in self.knowledge_base["general"]:
            subject = question_match.group(2)
            return f"Yo, man's clueless about {subject}, you feel me? What's the answer, fam?"

        return None

    def learn(self, subject, learned_response, name):
        if not any(word in subject.lower() for word in self.banned_words):
            if name not in self.user_learned_info:
                self.user_learned_info[name] = {}
            self.user_learned_info[name][subject.lower()] = learned_response
            self.save_learned_info()
            return True
        return False

    def categorize_learned_info(self, subject):
        tech_keywords = ["computer", "internet", "software", "hardware", "programming", "code"]
        science_keywords = ["physics", "chemistry", "biology", "astronomy", "math"]
        if any(keyword in subject.lower() for keyword in tech_keywords):
            return "tech"
        elif any(keyword in subject.lower() for keyword in science_keywords):
            return "science"
        else:
            return "general"

    def get_fallback_response(self, user_input):
        fallbacks = [
            "Yo, that's a bit confusing, fam. Can you break it down for me?",
            "Man's not sure what you mean, bruv. Can you say it differently?",
            "That's peak, I don't get it. What you trying to say, fam?",
            "You've lost me there, blud. Can you explain it another way?",
            f"Oi, {self.name}'s a bit confused. What you on about, fam?",
        ]
        return random.choice(fallbacks)

    def ask_for_more_info(self, user_input):
        question_words = ["what", "where", "when", "who", "why", "how"]
        for word in question_words:
            if user_input.lower().startswith(word):
                return f"Yo, can you give me more info about {user_input}? Man's trying to learn, you get me?"
        return None

    def get_greeting_response(self, name):
        responses = [
            f"Yo {name}! What's good?",
            f"Sup {name}! How you living?",
            f"Hey {name}! Everything blessed?",
            f"Wagwan {name}! How's it going?",
            f"Oi oi {name}! What's the latest?",
            f"Alright {name}? How you keeping?",
            f"Safe {name}! What's the vibe today?",
            f"Yo yo {name}! How's life treating you?"
        ]
        return random.choice(responses)

def main():
    chatbot = SecureRoadmanAI()
    name = input("Yo, what's your name, fam? ")
    print("RoadmanAI:", chatbot.greet(name))
    
    while True:
        user_input = input(f"{name}: ").strip()
        
        response = chatbot.respond(user_input, name)
        if response == "farewell":
            print("RoadmanAI:", chatbot.farewell())
            break
        
        print("RoadmanAI:", response)
        
        if response.startswith("Yo, can you give me more info"):
            additional_info = input("You: ").strip()
            learned_response = chatbot.try_learn_from_input(additional_info, name)
            if learned_response:
                print("RoadmanAI:", learned_response)
            else:
                print("RoadmanAI: Safe, maybe next time, fam.")

if __name__ == "__main__":
    main()