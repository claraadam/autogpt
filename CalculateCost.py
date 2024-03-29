class CalculateCost:
    def __init__(self):
        pass
    def Calculate(self,prompt_tokens, completion_tokens):
        prompt_cost = prompt_tokens * 0.0005 / 1000
        completion_cost = completion_tokens * 0.0015 / 1000
        cost = prompt_cost + completion_cost
        return cost