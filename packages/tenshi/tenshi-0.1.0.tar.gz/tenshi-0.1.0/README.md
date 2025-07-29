# Tenshi

**Tenshi** is a lightweight Gemini AI API wrapper designed for speed, reliability, and simplicity — especially for users relying on free API keys.

### 🔥 Features

- 🔁 **API Key Rotation** – Auto-switches between multiple keys to bypass rate limits  
- 💬 **System Prompt Support** – Define a system role for consistent responses  
- 🎛️ **Custom Temperature / Top-P** – Fine-tune creativity and randomness  
- 🆓 **Built for Free API Users** – Works around quota and rate issues  

---

### ✨ Installation
```
pip install tenshi
```
---

### 🚀 Quick Example
```
from tenshi import Tenshi

bot = Tenshi(api_keys=["your_api_key"])
bot.set_system("You are a helpful assistant.")
response = bot.generate("Hello!")
print(response)
```
---

### 📦 Use Cases

- Avoid rate limits with free or limited API keys  
- Chain multiple keys for reliability  
- Add system prompts for role-based responses (e.g., tutor, assistant, etc.)  
- Quickly prototype chatbots or AI tools using Gemini  

---

### 👤 Author

Made with purpose by **[@rubinexe](https://pypi.org/user/rubinexe/)**

---

### ⚖️ License

MIT License
