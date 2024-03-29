import os 
from time import gmtime, strftime
class SaveChat:
    def __init__(self):
        self.actual_time = strftime("%Y-%m-%d %H-%M-%S", gmtime())
        if not os.path.exists("output"):
                os.makedirs("output")
        self.file = f'output/chat_history{self.actual_time}.txt'

    def save_conversation(self,file,chat):
        with open(file, 'a') as f:
            f.write(chat)


    
