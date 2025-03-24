import requests
import time
from collections import deque
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

class AutocompleteExtractor:
    def __init__(self):
        self.base_url = "http://35.200.185.69:8000/v1/autocomplete"
        self.found_names = set()
        self.lock = threading.Lock()
        self.request_count = 0
        self.rate_limit_delay = 1.0
        self.max_workers = 3
        self.session = requests.Session()
        
    def make_request(self, query):
        """Handle API requests with rate limiting"""
        while True:
            try:
                with self.lock:
                    self.request_count += 1
                
                response = self.session.get(self.base_url, params={"query": query}, timeout=10)
                
                if response.status_code == 429:
                    time.sleep(self.rate_limit_delay)
                    self.rate_limit_delay *= 2
                    continue
                
                self.rate_limit_delay = max(1.0, self.rate_limit_delay / 2)
                return response.json().get('suggestions', []) if response.status_code == 200 else []
                    
            except requests.exceptions.RequestException:
                time.sleep(self.rate_limit_delay)
                self.rate_limit_delay *= 2
    
    def process_prefix(self, prefix):
        """Process prefix and return new prefixes"""
        suggestions = self.make_request(prefix)
        new_prefixes = set()
        
        with self.lock:
            for suggestion in suggestions:
                if suggestion not in self.found_names:
                    self.found_names.add(suggestion)
                    if len(suggestion) > len(prefix):
                        new_prefixes.add(suggestion[:len(prefix)+1])
        
        return new_prefixes
    
    def extract_all_names(self):
        """Main extraction using parallel BFS"""
        queue = deque([""])
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            while queue:
                current_batch = [queue.popleft() for _ in range(len(queue))]
                futures = {executor.submit(self.process_prefix, prefix): prefix for prefix in current_batch}
                
                for future in as_completed(futures):
                    for prefix in future.result():
                        queue.append(prefix)
                
                time.sleep(0.5)
        
        return sorted(self.found_names)
    
    def save_results(self, filename="autocomplete_names.json"):
        """Save results to JSON file"""
        with open(filename, 'w') as f:
            json.dump(sorted(self.found_names), f, indent=2)

if __name__ == "__main__":
    extractor = AutocompleteExtractor()
    print("Starting extraction...")
    start_time = time.time()
    
    names = extractor.extract_all_names()
    
    print(f"\nCompleted in {time.time()-start_time:.2f}s")
    print(f"Names found: {len(names)}")
    print(f"API requests: {extractor.request_count}")
    extractor.save_results()
