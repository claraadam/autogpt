import json
import RecommendationEngine
import CalculateCost 
class Chatbot:
    def __init__(self,client,recommendation_engine):
        self.client = client
        self.recommendation_engine = recommendation_engine
        self.calculate_cost = CalculateCost.CalculateCost()
        self.prompt_tokens =0
        self.completion_tokens =0
        self.system_prompt = """
        You're a Breizh Telecom assistant, First, you ask several short questions individually in order to find the best IT product for the user.
        Then, you use this information in the Engine to recommend the user 2 products with the name, the description and the score.
        When it's done you have completed your goal.
        """
        self.system_message = {'role': 'system', 'content': self.system_prompt}
        self.function_message = {'role': 'function', 'name': 'Engine', 'content': ""}
        self.user_message = {'role': 'user', 'content': ""}
        self.assistant_message = {'role': 'assistant', 'content': ""}
        self.to_save = self.system_message['content'] + "\n"
        self.messages = [self.system_message]
    def ask_openai(self): 
        response = self.client.chat.completions.create(
            messages=self.messages,
            model="gpt-3.5-turbo-0125",
            temperature=0,
            frequency_penalty =1.5,
            functions = [
            {
                "name": "Engine",
                "description": "Retrieve a top 3 products and their details using the user informations",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The user information",
                        }
                    },
                    "required": ["query"],
                    "function_call":"Engine"
                }
            }
            ]
        )
        print(response)
        return response
    def process_dialogue(self,user_input):
        self.messages.append({'role' : 'user', 'content' : user_input})
        output = "Wait a minute I am looking for a product"
        response= self.ask_openai()
        response_completion = response.choices[0].message.content 
        if response_completion != None :
            self.messages.append({'role' : 'assistant', 'content' : response_completion})
            output = response_completion
    
        if dict(response.choices[0].message).get('function_call'):
            # Which function call was invoked
            function_called = response.choices[0].message.function_call.name
            print("je call une function")
            # Extracting the arguments
            function_args  = json.loads(response.choices[0].message.function_call.arguments)

            # Function names
            available_functions = {
                "Engine": self.recommendation_engine.Engine
            }
            function_to_call = available_functions[function_called]
            
            function_return = str(function_to_call( *list(function_args.values())))
            self.function_message["content"]= f"The call of engine returned : {function_return}"
            self.messages.append(self.function_message)
            self.prompt_tokens += response.usage.prompt_tokens
            self.completion_tokens+=response.usage.completion_tokens
        return output
    def manage_exit(self,output):
        word_list = output.split() 
        last_word=""
        if len(word_list)!=0:
            last_word = word_list[-1]
        if output == "FINISH" or last_word == "FINISH":
            cost = self.calculate_cost.Calculate(self.prompt_tokens, self.completion_tokens)
            print(f"The totals cost was {cost} $")
            exit()