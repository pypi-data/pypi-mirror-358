import base64
import airouter
from airouter.models import LLM, ImageURL, ChatCompletionContentPartImageParam, Messages


def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')


if __name__ == '__main__':
  base64_image = encode_image("...")
  messages = [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "Analyse this image"
        },
        {
          "type": "image_url",
          "image_url": {
            "url": f"data:image/jpeg;base64,{base64_image}"
          }
        }
      ]
     },
  ]

  output = airouter.StreamedCompletion.create(
    model=LLM.GPT_4o,
    temperature=0.0,
    messages=messages,
  )

