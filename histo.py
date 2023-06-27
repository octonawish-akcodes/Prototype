import requests
import csv
import json
import os
import sys
from urllib.parse import urlparse

OBJECT_SPECS = dict(
    checkouts=dict(
        patchset_files=[dict(url=True)],
    ),
    builds=dict(
        input_files=[dict(url=True)],
        output_files=[dict(url=True)],
        config_url=True,
        log_url=True,
    ),
    tests=dict(
        output_files=[dict(url=True)],
        log_url=True,
    ),
)

def extract_fields(spec, data, origin):
    """
    Extract values of fields from data according to a specification.

    Args:
        spec:   The specification of fields to extract the values from.
        data:   The data to extract the field values from.

    Returns:
        An array of tuples, where each tuple contains:
            * A tuple containing dictionary keys leading to the field
            * The field value
    """
    tuples = []

    if isinstance(spec, dict):
        for k, v in spec.items():
            if k in data:
                for t in extract_fields(v, data[k], origin):
                    tuples.append(((k,) + t[0], t[1]))
    elif isinstance(spec, list):
        assert len(spec) == 1
        for idx, d in enumerate(data):
            tuples += extract_fields(spec[0], d, origin)
    elif spec == True:
        return [(tuple(), data)]

    return tuples

# Folder path containing JSON files
folder_path = '/home/abhishek/Downloads/scri/sample_data/269.data.json'

# Prepare CSV file
csv_writer = csv.writer(sys.stdout)
csv_writer.writerow([
    'Origin', 'Field Path', 'URL', 'Status Code',
    'Content Type', 'File Extension', 'URL Length (Bytes)', 'Size'
])

URL_INFO_CACHE = {}
URL_PATH_SET = set()  # Track unique field path and URL combinations

# Helper function to extract URL and size
def get_url_info(url):
    if url not in URL_INFO_CACHE:
        try:
            if url.endswith('/'):
                status_code = 0
                content_type = ''
                size = ''
                extension = ''
                url_length = sys.getsizeof(url.encode('utf-8'))
            else:
                response = requests.head(url)
                status_code = response.status_code
                content_type = ''
                size = ''
                if status_code == 200:
                    content_type = response.headers.get('Content-Type')
                    size = response.headers.get('Content-Length')
                    extension = os.path.splitext(urlparse(url).path)[1]
                else:
                    extension = os.path.splitext(urlparse(url).path)[1]
                url_length = len(url.encode('utf-8'))

            URL_INFO_CACHE[url] = (status_code, content_type, size, extension, url_length)
        except requests.exceptions.RequestException:
            URL_INFO_CACHE[url] = (0, '', '', '', sys.getsizeof(url.encode('utf-8')))
    return URL_INFO_CACHE[url]

# Iterate over files in the folder
for filename in os.listdir(folder_path):
    if filename.endswith('.json'):
        file_path = os.path.join(folder_path, filename)
        
        # Read JSON file
        with open(file_path, 'r') as json_file:
            DATA = json.load(json_file)

        # For each object type and spec
        for obj_type, obj_spec in OBJECT_SPECS.items():
            print(obj_spec)
            # obj_type = "checkouts"
            # obj_spec = dict(patchset_files=[dict(url=True)]) 
            # For each object of that type
            for obj in DATA.get(obj_type, []):
                print(obj, obj_type)
                origin = obj.get("origin", "")
                print(origin)
                # Extract URLs
                # obj_spec = dict(patchset_files=[dict(url=True)]) 
                # obj = a checkout
                url_tuples = extract_fields(obj_spec, obj, origin)

                # Iterating through URL tuples
                for keys, url in url_tuples:
                    path = '.'.join(keys)
                    status_code, content_type, size, \
                        extension, url_length = get_url_info(url)

                    # Check for unique field path and URL combination
                    if (path, url) in URL_PATH_SET:
                        continue

                    URL_PATH_SET.add((path, url))

                    # Save URL info in CSV file
                    csv_writer.writerow([
                        origin,
                        path, url, status_code, content_type,
                        extension, url_length, size
                    ])

sys.stdout.flush()
