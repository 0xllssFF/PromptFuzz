from openai import OpenAI
import logging
import time
import concurrent.futures

from sentence_transformers import SentenceTransformer


class LLM:
    def __init__(self):
        self.model = None
        self.tokenizer = None

    def generate(self, prompt):
        raise NotImplementedError("LLM must implement generate method.")

    def predict(self, sequences):
        raise NotImplementedError("LLM must implement predict method.")


class OpenAILLM(LLM):
    def __init__(self,
                 model_path,
                 api_key=None,
                 system_message=None
                ):
        super().__init__()

        if not api_key.startswith('sk-'):
            raise ValueError('OpenAI API key should start with sk-')
        self.client = OpenAI(api_key = api_key)
        self.model_path = model_path
        self.post_prompt = None
        self.system_message = system_message if system_message is not None else "You are a helpful assistant."

    def generate(self, prompt, temperature=0, max_tokens=512, n=1, max_trials=10, failure_sleep_time=30, target=None):
        if target is None:
            messages = [
                {"role": "system", "content": self.system_message},
                {"role": "user", "content": prompt}
            ]
        else:
            self.system_message = target['pre_prompt']
            self.post_prompt = target['post_prompt']
            messages = [
                {"role": "system", "content": self.system_message},
                {"role": "user", "content": prompt},
                {"role": "user", "content": self.post_prompt}
            ]
        for _ in range(max_trials):
            try:
                results = self.client.chat.completions.create(
                    model=self.model_path,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    n=n,
                )
                return [results.choices[i].message.content for i in range(n)]
            except Exception as e:
                logging.warning(
                    f"OpenAI API call failed due to {e}. Retrying {_+1} / {max_trials} times...")
                time.sleep(failure_sleep_time)

        return [" " for _ in range(n)]

    def generate_batch(self, prompts, temperature=0, max_tokens=512, n=1, max_trials=10, failure_sleep_time=30, target=None):
        results = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(self.generate, prompt, temperature, max_tokens, n,
                                       max_trials, failure_sleep_time, target): prompt for prompt in prompts}
            for future in concurrent.futures.as_completed(futures):
                results.extend(future.result())
        return results


class LocalLLMMistral(LLM):
    def __init__(self,
                 model_path,
                 server_url,
                 api_key=None,
                 system_message=None
                ):
        super().__init__()

        self.client = OpenAI(base_url=server_url, api_key = 'empty')
        self.model_path = model_path
        self.post_prompt = None
        self.system_message = system_message if system_message is not None else "You are a helpful assistant."

    def generate(self, prompt, temperature=0, max_tokens=512, n=1, max_trials=10, failure_sleep_time=30, target=None):
        if target is None:
            messages = [
                {"role": "system", "content": self.system_message},
                {"role": "user", "content": prompt}
            ]
        else:
            self.system_message = target['pre_prompt']
            self.post_prompt = target['post_prompt']
            messages = [
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": self.post_prompt}
            ]
        for _ in range(max_trials):
            try:
                results = self.client.chat.completions.create(
                    model=self.model_path,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    n=n,
                )
                return [results.choices[i].message.content for i in range(n)]
            except Exception as e:
                logging.warning(
                    f"OpenAI API call failed due to {e}. Retrying {_+1} / {max_trials} times...")
                time.sleep(failure_sleep_time)

        return [" " for _ in range(n)]

    def generate_batch(self, prompts, temperature=0, max_tokens=512, n=1, max_trials=10, failure_sleep_time=30, target=None):
        results = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(self.generate, prompt, temperature, max_tokens, n,
                                       max_trials, failure_sleep_time, target): prompt for prompt in prompts}
            for future in concurrent.futures.as_completed(futures):
                results.extend(future.result())
        return results
    
    

class LocalLLMOpenAI(LLM):
    def __init__(self,
                 model_path,
                 server_url,
                 api_key=None,
                 system_message=None
                ):
        super().__init__()

        self.client = OpenAI(base_url=server_url, api_key = 'empty')
        self.model_path = model_path
        self.post_prompt = None
        self.system_message = system_message if system_message is not None else "You are a helpful assistant."

    def generate(self, prompt, temperature=0, max_tokens=512, n=1, max_trials=10, failure_sleep_time=30, target=None):
        if target is None:
            messages = [
                {"role": "system", "content": self.system_message},
                {"role": "user", "content": prompt}
            ]
        else:
            self.system_message = target['pre_prompt']
            self.post_prompt = target['post_prompt']
            messages = [
                {"role": "system", "content": self.system_message},
                {"role": "user", "content": prompt},
                {"role": "user", "content": self.post_prompt}
            ]
        for _ in range(max_trials):
            try:
                results = self.client.chat.completions.create(
                    model=self.model_path,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    n=n,
                )
                return [results.choices[i].message.content for i in range(n)]
            except Exception as e:
                logging.warning(
                    f"OpenAI API call failed due to {e}. Retrying {_+1} / {max_trials} times...")
                time.sleep(failure_sleep_time)

        return [" " for _ in range(n)]

    def generate_batch(self, prompts, temperature=0, max_tokens=512, n=1, max_trials=10, failure_sleep_time=30, target=None):
        results = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(self.generate, prompt, temperature, max_tokens, n,
                                       max_trials, failure_sleep_time, target): prompt for prompt in prompts}
            for future in concurrent.futures.as_completed(futures):
                results.extend(future.result())
        return results
    
    
class OpenAIEmbeddingLLM():
    def __init__(self, model_path=None, api_key=None):
        self.client = OpenAI(api_key = api_key)
        self.model_path = model_path
    
    def get_embedding(self, prompt):
        response = self.client.embeddings.create(
            input=prompt,
            model=self.model_path
        )
        
        return response.data[0].embedding

class OtherEmbeddingLLM():
    def __init__(self, model_path=None):
        self.model = SentenceTransformer("Alibaba-NLP/gte-Qwen2-1.5B-instruct", trust_remote_code=True).to('cuda')

    
    def get_embedding(self, prompt):

        embedding = self.model.encode(prompt)
        
        return embedding