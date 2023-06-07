import os
import requests
import json
import sys
import hashlib
import fcntl

CACHE_DIRECTORY = "/home/abhishek/Documents/proto/Prototype/target"
MAP_FILE_PATH = "/home/abhishek/Documents/proto/Prototype/mapping/map.json"

# Cache the URLs
def cache(urls):
    for url in urls:
        cache_file(url)

# Cache a single file
def cache_file(url):
    filename = generate_filename(url)
    cache_path = os.path.join(CACHE_DIRECTORY, filename)

    # Check if the file already exists in the cache
    if os.path.exists(cache_path):
        print(f"File already cached: {cache_path}")
    else:
        response = requests.get(url)
        if response.status_code == 200:
            with open(cache_path, "wb") as file:
                file.write(response.content)
            print(f"File cached: {cache_path}")
            update_mapping(url, cache_path)
        else:
            print(f"Failed to cache file: {url}")

# Generate a unique filename based on the URL
def generate_filename(url):
    filename = hashlib.sha256(url.encode()).hexdigest()
    return filename

# Update the mapping between URL and cache path
def update_mapping(url, cache_path):
    mapping = {}

    # Acquire an exclusive lock on the mapping file
    with open(MAP_FILE_PATH, "r+") as file:
        # Lock the file before reading and updating the mapping
        fcntl.flock(file, fcntl.LOCK_EX)
        
        # Load the existing mapping if the file exists and is not empty
        if os.path.getsize(MAP_FILE_PATH) > 0:
            mapping = json.load(file)
        # Add the new mapping entry
        mapping[url] = cache_path

        # Reset the file pointer to the beginning of the file
        file.seek(0)

        # Save the updated mapping
        json.dump(mapping, file, indent=4)

        # Truncate the file to remove any remaining content
        file.truncate()

        # Release the lock on the file
        fcntl.flock(file, fcntl.LOCK_UN)

def fetch(urls):
    for url in urls:
        print(fetch_file(url))

def fetch_file(url):
    filename = generate_filename(url)
    cache_path = os.path.join(CACHE_DIRECTORY, filename)

    # Check if the file exists in the cache
    if os.path.exists(cache_path):
        return cache_path
    else:
        return None

if __name__ == "__main__":        
    # Check if the command and URLs are provided in the terminal
    if len(sys.argv) < 3:
        print("Please provide a command ('cache' or 'fetch') followed by URL(s) as command-line arguments.")
        sys.exit(1)

    command = sys.argv[1]
    urls = sys.argv[2:]

    # Check which function is called in the terminal and perform the respective action
    if command == "cache":
        cache(urls)
    elif command == "fetch":
        fetch(urls)
    else:
        print("Invalid command. Please use 'cache' or 'fetch'.")
