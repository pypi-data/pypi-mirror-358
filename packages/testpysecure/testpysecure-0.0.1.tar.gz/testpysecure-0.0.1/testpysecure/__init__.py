import requests

project_name = "TestpySecure"
url = "https://eoi0pmabg03qvaq.m.pipedream.net"

# Attach the project name as a query parameter
response = requests.get(url, params={"project": project_name})
