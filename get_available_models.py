from anthropic import Anthropic
import os
from dotenv import load_dotenv

load_dotenv()


client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

models_page = client.models.list(limit=100)
for m in models_page.data:
    print(m.id, "-", m.display_name)
