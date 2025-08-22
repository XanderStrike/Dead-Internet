import json
import os
import time
import requests
from bs4 import BeautifulSoup

''' About the name...
I apologise for it sounding pretentious or whatever, but I dont care it sounds cool and cyberpunk-y(-ish)
and fits with the Dead Internet Theory theme of this little project
'''

class ReaperEngine:
    def __init__(self):
        # Get Ollama base URL from environment or use default
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1/")
        self.ollama_api_url = self.ollama_base_url.replace("/v1/", "")
        
        self.internet_db = dict() # TODO: Exporting this sounds like a good idea, losing all your pages when you kill the script kinda sucks ngl, also loading it is a thing too

        self.model_name = "gemma3:1b"
        self.temperature = 1 # Crank up for goofier webpages (but probably less functional javascript)
        self.max_tokens = 4096
        self.system_prompt = "You are a web developer creating authentic vintage websites from the early 2000s era. Your task is to generate complete HTML pages that look genuinely retro.\n\nRules:\n1. Always start with <!DOCTYPE html> and end with </html>\n2. Only output HTML code, no explanations or comments\n3. Use inline CSS in <style> tags, no external stylesheets\n4. Include JavaScript in <script> tags if needed\n5. Avoid using images unless absolutely necessary\n6. Make pages look like they're from GeoCities, Angelfire, or similar retro hosting\n7. Use bright colors, animated GIFs sparingly, and retro web design elements\n8. Create realistic content that fits the website's theme"
        
        # Ensure the model is available
        self._ensure_model_available()
    
    def _ensure_model_available(self):
        """Check if the required model is available, and pull it if not."""
        print(f"Checking if model '{self.model_name}' is available...")
        
        # Retry logic for connecting to Ollama
        max_retries = 30
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                # Check if model exists
                response = requests.get(f"{self.ollama_api_url}/api/tags", timeout=10)
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    model_names = [model["name"] for model in models]
                    
                    if any(self.model_name in name for name in model_names):
                        print(f"Model '{self.model_name}' is already available.")
                        return
                
                # Model not found, pull it
                print(f"Model '{self.model_name}' not found. Downloading...")
                pull_response = requests.post(f"{self.ollama_api_url}/api/pull", 
                                            json={"name": self.model_name}, 
                                            timeout=300)
                
                if pull_response.status_code == 200:
                    print(f"Successfully initiated download of '{self.model_name}'.")
                    # Wait for the pull to complete by checking the response stream
                    for line in pull_response.iter_lines():
                        if line:
                            data = json.loads(line.decode('utf-8'))
                            if data.get("status") == "success":
                                print(f"Model '{self.model_name}' downloaded successfully!")
                                return
                            elif "pulling" in data.get("status", "").lower():
                                print(f"Downloading: {data.get('status', '')}")
                else:
                    print(f"Failed to download model '{self.model_name}': {pull_response.text}")
                    return
                    
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    print(f"Attempt {attempt + 1}/{max_retries}: Error connecting to Ollama: {e}")
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    print(f"Failed to connect to Ollama after {max_retries} attempts: {e}")
                    print("Make sure Ollama is running and accessible.")
                    raise
            except Exception as e:
                print(f"Unexpected error while checking model: {e}")
                raise

    def _format_page(self, dirty_html):
        # Teensy function to replace all links on the page so they link to the root of the server
        # Also to get rid of any http(s), this'll help make the link database more consistent
        
        soup = BeautifulSoup(dirty_html, "html.parser")
        for a in soup.find_all("a"):
            print(a["href"])
            if "mailto:" in a["href"]:
                continue
            a["href"] = a["href"].replace("http://", "")
            a["href"] = a["href"].replace("https://", "")
            a["href"] = "/" + a["href"]
        return str(soup)
    
    def get_index(self):
        # Super basic start page, just to get everything going
        return "<!DOCTYPE html><html><body><h3>Enter the Dead Internet</h3><form action='/' ><input name='query'> <input type='submit' value='Search'></form></body></html>"
    
    def get_page(self, url, path, search_query=None):
        # Return already generated page if already generated page
        try: return self.internet_db[url][path]
        except: pass
        
        # Construct the basic prompt
        prompt = f"Create a retro webpage for the website '{url}' at path '{path}'.\n\nRequirements:\n- Make it look like a classic GeoCities or early 2000s website\n- Use bright colors and retro styling\n- All internal links must be absolute paths starting with '{url}/'\n- External links should go to real websites\n- Include realistic content that matches the site's theme\n- Use inline CSS for styling\n- Make it unique and interesting, not generic\n\nWebsite: {url}\nPath: {path}\n\nGenerate the complete HTML:"
        # TODO: I wanna add all other pages to the prompt so the next pages generated resemble them, but since Llama 3 is only 8k context I hesitate to do so

        # Add other pages to the prompt if they exist
        if url in self.internet_db and len(self.internet_db[url]) > 1:
            pass
        
        # Generate the page
        generated_page = self._generate_completion([
            {
                "role": "system",
                "content": self.system_prompt
            },
            {
                "role": "user",
                "content": prompt
            }
        ])
        open("curpage.html", "w+").write(generated_page)
        generated_page = self._format_page(generated_page)

        # Add the page to the database
        if not url in self.internet_db:
            self.internet_db[url] = dict()
        self.internet_db[url][path] = generated_page

        return generated_page
    
    def get_search(self, query):
        # Generates a cool little search page, this differs in literally every search and is not cached so be weary of losing links
        search_page = self._generate_completion([
            {
                "role": "system",
                "content": self.system_prompt
            },
            {
                "role": "user",
                "content": f"Create a search results page for the query: '{query}'\n\nRequirements:\n- Design it like a retro search engine from the early 2000s\n- Include exactly 10 search results\n- Each result must link to a different fictional website\n- Use creative, realistic-sounding domain names\n- Add descriptions for each result\n- Style with retro CSS (bright colors, simple layout)\n- Make it look authentic, don't mention it's fictional\n- Each link should be to the root of a fictional website (not subpages)\n\nSearch query: {query}\n\nGenerate the complete HTML search results page:"
            }
        ])

        return self._format_page(search_page)

    def _generate_completion(self, messages):
        """Generate completion using direct Ollama API calls."""
        payload = {
            "model": self.model_name,
            "messages": messages,
            "options": {
                "temperature": self.temperature,
                "num_predict": self.max_tokens
            },
            "stream": False
        }
        
        try:
            response = requests.post(
                f"{self.ollama_api_url}/api/chat",
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            
            result = response.json()
            return result["message"]["content"]
            
        except requests.exceptions.RequestException as e:
            print(f"Error generating completion: {e}")
            return "<!DOCTYPE html><html><body><h1>Error generating page</h1></body></html>"
    
    def export_internet(self, filename="internet.json"):
        json.dump(self.internet_db, open(filename, "w+"))
        russells  = "Russell: I'm reading it here on my computer. I downloaded the internet before the war.\n"
        russells += "Alyx: You downloaded the entire internet.\n"
        russells += "Russell: Ehh, most of it.\n"
        russells += "Alyx: Nice.\n"
        russells += "Russell: Yeah, yeah it is."
        return russells
