from google.cloud import storage
import hashlib
import requests
from urllib.parse import unquote

class Cache:
    def __init__(self, bucket_name, max_store_size):
        """
        Initialize a cache client.
        Args:
            bucket_name:    The name of the GCS bucket containing the cache.
            max_store_size: Maximum size the file can have to be stored.
        """
        self.bucket_name = bucket_name
        self.max_store_size = max_store_size
        self.client = storage.Client()

    def store(self, url):
        """
        Attempt to store a URL in the cache. The URL contents is not
        downloaded if it's already in the cache or if it doesn't match the
        requirements (max_store_size).
        Args:
            url:    The URL to try to cache.
        """
        object_name = self._format_object_name(url)
        blob = self.client.bucket(self.bucket_name).blob(object_name)

        if blob.exists():
            print(f"URL '{url}' is already cached.")
            return

        try:
            # Performing HEAD request first
            response = requests.head(url)
            if response.status_code == 200:
                content_type = response.headers["Content-Type"]
                
                # Check the size of the content before downloading
                content_length = response.headers.get("Content-Length")
                if content_length is not None:
                    content_length = int(content_length)
                    if content_length > self.max_store_size:
                        print(f"URL '{url}' exceeds the maximum allowed size and cannot be cached.")
                        return
                
                # Perform the GET request to download the contents
                response = requests.get(url)
                if response.status_code == 200:
                    contents = response.content
                    
                    # Extract the original filename from the URL
                    original_filename = self._extract_filename(url)

                    blob.upload_from_string(
                    contents,
                    content_type=content_type
                    )
                    blob.content_disposition = f'inline; filename="{original_filename}"'
                    blob.patch()
                
                    print(f"URL '{url}' cached successfully.")
                else:
                    print(f"Failed to download URL '{url}'. Status code: {response.status_code}")
            else:
                print(f"Failed to download URL '{url}'. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error occurred while downloading URL '{url}': {str(e)}")

    def _format_object_name(self, url):
        """
        Format a cache object name for a given (potentially) cached URL.
        Does not access the GCS storage.
        Args:
            url:    The (potentially) cached URL to format the object name for.
        Returns:
            The object name of the (potentially) cached URL.
        """
        # Generate a unique hash for the URL as the object name
        return hashlib.sha256(url.encode()).hexdigest()
    
    def _extract_filename(self, url):
        """
        Extract the filename from a given URL.
        Args:
            url:    The URL to extract the filename from.
        Returns:
            The extracted filename from the URL.
        """
        decoded_url = unquote(url)
        return decoded_url.rsplit('/', 1)[-1]

    def _format_public_url(self, url):
        """
        Format a public URL for a given (potentially) cached URL.
        Does not access the GCS storage.
        Args:
            url:    The (potentially) cached URL to format the public URL for.
        Returns:
            The public URL of the (potentially) cached URL.
        """
        return f"https://storage.googleapis.com/{self.bucket_name}/{self._format_object_name(url)}"

    def map(self, url):
        """
        Map a URL to the public URL of its cached contents, if it is cached.
        Args:
            url:    The potentially-cached URL to map.
        Returns:
            The public URL of the cached content, if the URL is cached.
            None if the URL is not cached.
        """
        object_name = self._format_object_name(url)
        blob = self.client.bucket(self.bucket_name).blob(object_name)

        if blob.exists():
            return self._format_public_url(url)
        else:
            return None

    def is_stored(self, url):
        """
        Check if a URL is stored in the cache or not.
        Args:
            url:    The URL to check.
        Returns:
            True if the URL is cached, False if not.
        """
        return self.map(url) is not None

    def fetch(self, url):
        """
        Retrieve the contents of a URL if cached.
        Args:
            url:    The URL to retrieve the cached content of.
        Returns:
            The binary contents of the cached URL or None if not cached.
        """
        object_name = self._format_object_name(url)
        blob = self.client.bucket(self.bucket_name).blob(object_name)

        if blob.exists():
            return blob.download_as_bytes()
        else:
            return None

# Example usage:
cache = Cache("cache_file_storage", 5 * 1024 * 1024)

# Cache these URLs
url_list = ["https://www.gutenberg.org/files/1342/old/pandp12p.pdf", "https://www.dwsamplefiles.com/?dl_id=176", "http://storage.kernelci.org/images/rootfs/buildroot/buildroot-baseline/20230120.0/armel/rootfs.cpio.gz"]
for url in url_list:
    cache.store(url)
