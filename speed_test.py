import time
import requests
import json
from colorama import Fore, init

init(autoreset=True)

URL = "https://ai.api-rapnss.workers.dev"

def test_cors():
    print(Fore.CYAN + "Testing OPTIONS (CORS Preflight) latency...")
    start = time.time()
    resp = requests.options(URL)
    duration = time.time() - start
    print(f"OPTIONS Status: {resp.status_code}")
    print(f"OPTIONS Latency: {duration:.3f}s")
    return duration

def test_chat_simple(model=None):
    payload = {
        "messages": [{"role": "user", "content": "Hi"}],
        "max_tokens": 10
    }
    if model:
        payload["model"] = model
    
    label = f"POST (Model: {model if model else 'Default'})"
    print(Fore.CYAN + f"Testing {label} latency...")
    
    start = time.time()
    try:
        resp = requests.post(URL, json=payload, timeout=90)
        duration = time.time() - start
        if resp.status_code == 200:
            print(Fore.GREEN + f"{label} Success: {duration:.3f}s")
            # print(f"Response: {resp.json().get('response')}")
        else:
            print(Fore.RED + f"{label} Failed ({resp.status_code}): {resp.text}")
    except Exception as e:
        duration = 90
        print(Fore.RED + f"{label} Timeout/Error: {e}")
    
    return duration

if __name__ == "__main__":
    print(Fore.YELLOW + "=== AI Worker Speed Test Report ===")
    
    cors_lat = test_cors()
    
    # Warmer run
    print("\nWarming up connection...")
    test_chat_simple()
    
    # Benchmarking
    print("\nStarting Benchmark...")
    l1 = test_chat_simple() # Default
    l2 = test_chat_simple("@cf/meta/llama-3.1-8b-instruct") # Llama 3.1
    l3 = test_chat_simple("@cf/tinyllama/tinyllama-1.1b-chat-v1.0") # Smaller model for comparison
    
    print("\n" + Fore.YELLOW + "=== Summary Results ===")
    print(f"CORS (OPTIONS): {cors_lat:.3f}s")
    print(f"Llama 3.1 8B (Default): {l1:.3f}s")
    print(f"Llama 3.1 8B (Explicit): {l2:.3f}s")
    print(f"TinyLlama (Smallest): {l3:.3f}s")
