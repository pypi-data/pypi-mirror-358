# HWC BGR 888 Image to Base64 URI

A specialized utility for converting OpenCV-compatible HWC BGR 888 images to Base64-encoded data URIs. Can be used with the OpenAI Chat Completions API.

## Usage with OpenAI Chat Completions API

```python
from __future__ import print_function
import cv2

from hwc_bgr_888_image_to_base64_uri import hwc_bgr_888_image_to_base64_uri
from openai import OpenAI


# Initialize client
client = OpenAI(
    # For Ollama local endpoint
    base_url='http://localhost:11434/v1/',
    api_key='ollama', # Required parameter (ignored by Ollama)
)

# 1. Load image using OpenCV (native BGR format)
image = cv2.imread('input.jpg')

# 2. Convert to API-compliant URI (auto-resizes to 512px longest edge)
uri = hwc_bgr_888_image_to_base64_uri(
    image,
    max_long_edge=512, # Recommended for most vision models
    output_format_extension=u'.jpg' # Or u'.png' for quality
)

# 3. Structure chat completions request
response = client.chat.completions.create(
    model=u"llava",
    messages=[
        {
            u"role": u"user",
            u"content": [
                {u"type": u"text", u"text": u"What's in this image?"},
                {
                    u"type": u"image_url",
                    u"image_url": {
                        u"url": uri # Our generated URI
                    }
                }
            ]
        }
    ]
)

print(response.choices[0].message.content)
```

For more information:

- https://platform.openai.com/docs/api-reference/chat/create
- https://github.com/ollama/ollama/blob/main/docs/openai.md#curl

## Contributing

Contributions are welcome! Please submit pull requests or open issues on the GitHub repository.

## License

This project is licensed under the [MIT License](LICENSE).
