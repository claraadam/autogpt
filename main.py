from openai import OpenAI
import pandas as pd
import os 
from scipy import spatial 
import json
from time import gmtime, strftime
import web_scraping


def save():
    actual_time = strftime("%Y-%m-%d %H-%M-%S", gmtime())
    if not os.path.exists("output"):
            os.makedirs("output")
    file = f'output/chat_history{actual_time}.txt'
    return file

def save_chat(file,chat):
    with open(file, 'a') as f:
        f.write(chat)
            
def get_embedding(text, model="text-embedding-3-small"):
        text = text.replace("\n", " ")
        return client.embeddings.create(input=[text], model=model).data[0].embedding

def calculate_cost(prompt_tokens,completion_tokens):
        prompt_cost = prompt_tokens * 0.0005 / 1000
        completion_cost = completion_tokens * 0.0015 / 1000
        cost = prompt_cost + completion_cost
        return cost

def create_df(text):
        if not os.path.exists("data"):
            os.makedirs("data")

        entries = text.split('\n\n')
        data = {'restaurant': [], 'address': [], 'description': [], 'ada_embedding': []}

        for entry in entries:
            lines = entry.split('\n')
            if lines: 
            
                title_line = [line for line in lines if line.startswith('Titre:')][0]
                title = title_line.split('Titre: ')[1]
                
                address_line = [line for line in lines if line.startswith('Adresse:')][0]
                address = address_line.split('Adresse: ')[1]

                description = ' '.join([line.split(': ')[1] for line in lines if line.startswith('Description:')])
                content = title + address + description
                embedding = get_embedding(content, model='text-embedding-3-small')
                data['restaurant'].append(title)
                data['address'].append(address)
                data['description'].append(description)
                data['ada_embedding'].append(embedding)

        df = pd.DataFrame(data)
        df.to_csv('data/restaurants.csv', index=False)

# Define a function to retrieve top restaurant recommendations based on user input
def restaurant_tool(query):
        """Returns a list of strings and relatednesses, sorted from most related to least."""
        relatedness_fn=lambda x, y: 1 - spatial.distance.cosine(x, y)
        top_n=3
        embedding_model='text-embedding-3-small'
        df = pd.read_csv("data/restaurants.csv")
        query_embedding_response = client.embeddings.create(
            model=embedding_model,
            input=query,
        )
        query_embedding = query_embedding_response.data[0].embedding
        df['ada_embedding'] = df['ada_embedding'].apply(eval) 
        strings_and_relatednesses = [
            (row["restaurant"], row["address"], row["description"], relatedness_fn(query_embedding, row["ada_embedding"]))
            for i, row in df.iterrows()
        ]
        strings_and_relatednesses.sort(key=lambda x: x[3], reverse=True)
        result_dict = {
        entry[0]: {
            'adresse': entry[1],
            'description': entry[2],
            'score': entry[3]
        }
        for entry in strings_and_relatednesses[:top_n]
        }
        return result_dict

class Chatbot:
    def __init__(self):
        self.prompt_tokens =0
        self.completion_tokens =0
        self.chat_history = ""
        self.system_prompt = """
        You're an ai assistant, FIRST you ask several questions individually in order to find the best restaurant for the user.
        THEN you use this information in the restaurant tool to recommend the user 2 restaurants with the name, the adress the description and the score.
        If you think that it won't match the customer intent, explain why.
        When it's done you have completed your goal your response must be FINISH.
        """
        self.system_message = {'role': 'system', 'content': self.system_prompt}
        self.function_message = {'role': 'function', 'name': 'restaurant_tool', 'content': ""}
        self.user_message = {'role': 'user', 'content': ""}
        self.to_save = self.system_message['content'] + "\n"
        self.messages = [self.system_message]

    def ask_openai(self,user_input):   
        self.to_save+= user_input + "\n"
        self.messages.append({'role': 'user', 'content': user_input})
        response = client.chat.completions.create(
            messages=self.messages,
            model="gpt-3.5-turbo-0125",
            temperature=0,
            frequency_penalty =1.5,
            functions = [
            {
                "name": "restaurant_tool",
                "description": "Retrieve a top 3 restaurants and their details using the user informations",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "chat_history": {
                            "type": "string",
                            "description": "The chat_history variable",
                        }
                    },
                    "required": ["chat_history"],
                    "function_call":"restaurant_tool"
                }
            }
            ]
        )
        chatbot_response = response.choices[0].message
        if chatbot_response.content != None :
             self.messages.append({'role' : 'assistant', 'content' : chatbot_response.content})
             self.to_save += chatbot_response.content + "\n"
        self.prompt_tokens += response.usage.prompt_tokens
        self.completion_tokens+=response.usage.completion_tokens
        return chatbot_response

if __name__ == "__main__":

    client = OpenAI()
    chatbot = Chatbot()
    file = save()

    if os.path.exists("restaurants.txt"):
        with open("restaurants.txt", "r", encoding="utf-8") as f:
                text = f.read()
                print("File loaded")
    else :
        content = web_scraping.get_content()
        with open("restaurants.txt", "w") as f:
             f.write(content)

    if not os.path.exists("data/restaurants.csv"):
            chatbot.create_df(text)
            print("vectorization completed")

    while True:
        user_input = input("Vous: ")
        response= chatbot.ask_openai(user_input)

        if response.content != None :
            response_message = response.content
            
        else : 
             response_message = "I'm looking for the best restaurant"
            
        # Process function call if present in the API response
        if dict(response).get('function_call'):
    
            function_called = response.function_call.name
            
            function_args  = json.loads(response.function_call.arguments)
            
            available_functions = {
                "restaurant_tool": restaurant_tool
            }
            function_to_call = available_functions[function_called]
            
            function_return = str(function_to_call(*list(function_args.values())))
            chatbot.function_message["content"]= f"The call of restaurant_tool returned : {function_return}"
            chatbot.messages.append(chatbot.function_message)

        # Save chat history 
        save_chat(file,chatbot.to_save)  
        chatbot.to_save ="" 
        print(f"Chatbot: {response_message}")

        # Check for finishing conditions
        word_list = response_message.split() 
        last_word = word_list[-1]
        if response_message == "FINISH" or last_word == "FINISH":
            cost = calculate_cost(chatbot.prompt_tokens, chatbot.completion_tokens)
            print(f"The totals cost was {cost} $")
            save_chat(file,chatbot.to_save) 
            save_chat(file,f"The totals cost was {cost} $")  
            exit()
       
        