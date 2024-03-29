from scipy import spatial 
import pandas as pd
class RecommendationEngine():
        def __init__(self,client):
            self.client = client
            self.relatedness_fn=lambda x, y: 1 - spatial.distance.cosine(x, y)
            self.top_n = 3
            self.embedding_model='text-embedding-3-small'

        def Engine(self,query):
            df = pd.read_csv("data/products.csv")
            query_embedding_response = self.client.embeddings.create(
                model=self.embedding_model,
                input=query,
            )
            query_embedding = query_embedding_response.data[0].embedding
            df['ada_embedding'] = df['ada_embedding'].apply(eval) 
            strings_and_relatednesses = [
                (row['product'], row['supplier'], row['client'], row['usage'],row['description'], self.relatedness_fn(query_embedding, row["ada_embedding"]))
                for i, row in df.iterrows()
            ]
            strings_and_relatednesses.sort(key=lambda x: x[5], reverse=True)
            result_dict = {
            entry[0]: {
                'product': entry[0],
                'supplier' : entry[1], 
                'client': entry[2],
                'usage' : entry[3],
                'description': entry[4],
                'score': entry[5]
            }
            for entry in strings_and_relatednesses[:self.top_n]
            }
            return result_dict