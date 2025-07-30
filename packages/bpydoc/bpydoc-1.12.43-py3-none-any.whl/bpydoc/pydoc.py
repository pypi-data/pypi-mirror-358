class BPydoc:
    def __init__(self, api_key):
        from groq import Groq  # assumes Groq SDK is installed
        self.client = Groq(api_key=api_key)

    def send_prompt(self, prompt, model="llama-3.3-70b-versatile"):
        """
        Sends a prompt to the Groq API and returns the response.

        :param prompt: The user prompt to send to the API.
        :param model: The model to use for the API request.
        :return: The response text from the API.
        """
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=model
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            print("Error occurred while communicating with the Groq API:", e)
            raise RuntimeError(f"An error occurred while communicating with the Groq API: {e}")