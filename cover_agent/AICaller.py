import time
import litellm

class AICaller:
    def __init__(self, model: str, api_base: str = ""):
        """
        Initializes an instance of the AICaller class.

        Parameters:
            model (str): The name of the model to be used.
            api_base (str): The base API url to use in case model is set to Ollama or Hugging Face
        """
        self.model = model
        self.api_base = api_base

    def call_model(self, prompt: dict, max_tokens=4096):
        """
        Call the language model with the provided prompt and retrieve the response.

        Parameters:
            prompt (dict): The prompt to be sent to the language model.
            max_tokens (int, optional): The maximum number of tokens to generate in the response. Defaults to 4096.

        Returns:
            tuple: A tuple containing the response generated by the language model, the number of tokens used from the prompt, and the total number of tokens in the response.
        """
        if 'system' not in prompt or 'user' not in prompt:
            raise KeyError("The prompt dictionary must contain 'system' and 'user' keys.")
        if prompt['system'] == "":
            messages = [{"role": "user", "content": prompt['user']}]
        else:
            messages = [{"role": "system", "content": prompt['system']},
                        {"role": "user", "content": prompt['user']}]

        # API base exception for Ollama and Hugging Face models
        if "ollama" in self.model or "huggingface" in self.model:
            response = litellm.completion(model=self.model, api_base=self.api_base, messages=messages, max_tokens=max_tokens, stream=True) 
        else :
            response = litellm.completion(model=self.model, messages=messages, max_tokens=max_tokens, stream=True)

        chunks = []
        print("Streaming results from LLM model...")
        try:
            for chunk in response:
                print(chunk.choices[0].delta.content or "", end="", flush=True)
                chunks.append(chunk)
                time.sleep(0.01)  # Optional: Delay to simulate more 'natural' response pacing
        except Exception as e:
            print(f"Error during streaming: {e}")
        print("\n")

        model_response = litellm.stream_chunk_builder(chunks, messages=messages)

        # Returns: Response, Prompt token count, and Response token count
        return model_response['choices'][0]['message']['content'], int(model_response['usage']['prompt_tokens']), int(model_response['usage']['completion_tokens'])
