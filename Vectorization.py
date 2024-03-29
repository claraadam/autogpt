import os 
import pandas as pd 
class Vectorization : 
    def __init__(self,client):
         self.client = client
         
    def get_embedding(self,text, model="text-embedding-3-small"):
            text = text.replace("\n", " ")
            return self.client.embeddings.create(input=[text], model=model).data[0].embedding


    def create_df(self,text):
            if not os.path.exists("data"):
                os.makedirs("data")

            # Split text into restaurant entries
            entries = text.split('\n\n')
            data = {'product': [], 'supplier': [], 'client': [], 'usage': [],'description': [], 'ada_embedding': []}

            for entry in entries:
                technical = ""
                lines = entry.split('\n')
                if lines: 
                    # Extract restaurant name, address, and description
                    print(lines)
                    for line in lines :
                        if line.startswith('Product'):
                            product = line
                        if line.startswith('Supplier'):
                            supplier = line 
                        if line.startswith('Client'):
                            client = line
                        if line.startswith('Usage'):
                            usage = line 
                        if line.startswith('Description'):
                            description = line 
            
                        
                    content = product + supplier + client + usage+ description
                    print(content)
                    # Generate embedding for the description
                    embedding = self.get_embedding(content, model='text-embedding-3-small')
                    # Append data to the dictionary
                    data['product'].append(product)
                    data['supplier'].append(supplier)
                    data['client'].append(client)
                    data['usage'].append(usage)
                    data['description'].append(description)
                    data['ada_embedding'].append(embedding)

            # Create DataFrame and save to CSV
            df = pd.DataFrame(data)
            df.to_csv('data/products.csv', index=False)