import requests

API_KEY = '6b70cf40873c5d6e706e5aa87a5ceab97ac8032b'
BASE_URL = 'https://api.uexcorp.com/'  # Replace with actual base URL

# Example function to test the API

def test_api(endpoint):
    url = BASE_URL + endpoint
    headers = {'Authorization': f'Bearer {API_KEY}'}
    response = requests.get(url, headers=headers)
    return response.json()

if __name__ == '__main__':
    # Replace 'your_endpoint' with actual endpoint you want to test
    result = test_api('your_endpoint')
    print(result)