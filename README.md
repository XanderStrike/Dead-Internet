# Dead-Internet
So we all know the classic [Dead Internet Theory](https://en.wikipedia.org/wiki/Dead_Internet_theory), and if you're reading this I assume you at least know what an LLM is. Need I say much more? Yeah of course!

This is a little project I threw together in a couple hours that lets you surf a completely fake web! You run a search query in the only non-generated page `/` and it generates a search results page with fake links that lead to fake websites that lead to more fake websites! 
It's not perfect, not by a long shot, but it works well enough for me to spend like an hour just going through it and laughing at what it makes.

If you encounter any issues with the search results page, reload and it'll generate a new page. If you get any issues with the other generated pages then try make slight adjustments to the URL to get a different page, right now there isn't yet a way to regenerate a page.

Also when you navigate to the `/_export` path or kill the server, the JSON of your current internet will be saved to the file `internet.json` in the root of the project. Right now you can't load it back yet but maybe I'll add that in the future if I want, or you could fork it and add it yourself the code isn't very complicated at all.

## How do I run this???

### Option 1: Docker Compose (Recommended)
The easiest way to run this project is with Docker Compose, which will automatically set up both Ollama and the Dead Internet app:

1. Make sure you have Docker and Docker Compose installed
2. Clone this repository
3. Run: `docker-compose up`
4. Wait for Ollama to download the model (this may take a few minutes on first run)
5. Navigate to http://localhost:8080 and have fun!

The Docker setup will automatically pull the `gemma3:1b` model and configure everything for you.

### Option 2: Manual Setup
If you prefer to run things manually, first install Ollama [here](https://ollama.com/download), then pull your model of choice. The default model is now [Gemma 3 1B](https://ollama.com/library/gemma3:1b) which works well and is lightweight. You can also use [Llama 3 8B Instruct](https://ollama.com/library/llama3) which works really well and is very impressive for an 8B model. If you don't want to use Ollama you can use any other OpenAI-compatible server by modifying the `OLLAMA_BASE_URL` environment variable.

Due to popular demand and it not being 12am anymore I finally added a requirements.txt file! Now instead of manually installing dependencies you can just run `pip install -r requirements.txt` in the root of the project and it'll install them all for you!

(If you want to manually install dependencies, follow these instructions) Next you'll need to install Python if you don't already have it, I run Python 3.10.12 (came with my Linux Mint install), then the libraries you'll need are:
- [BeautifulSoup4](https://pypi.org/project/beautifulsoup4/)
- [Flask](https://pypi.org/project/Flask/)
- [Requests](https://pypi.org/project/requests/)

Once those are installed, simply run the main.py file and navigate to http://127.0.0.1:8080 or whatever URL Flask gives you and have fun!

## Inspiration
I'll admit it, I'm not the most creative person. I got this idea from [this reddit comment on r/localllama](https://new.reddit.com/r/LocalLLaMA/comments/1c6ejb8/comment/l02eeqx/), so thank you very much commenter!
