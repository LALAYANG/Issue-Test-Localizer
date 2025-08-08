import os

import openai


def prompt_model(model_name, prompt, temperature=0.7):
    client = openai.OpenAI(
        api_key=os.environ["OPENAI_API_KEY"],
        base_url=os.environ["MODEL_SERVING_URL"],
    )

    response = client.chat.completions.create(
        model=model_name,
        temperature=temperature,
        messages=[{"role": "user", "content": prompt}],
    )
    print(response)
    return response.choices[0].message.content.strip()
