import requests
import os

def test_get_pet_by_id():
	response = requests.get('http://0.0.0.0:8080/pet/0')
	assert response.status_code == 200


def test_update_pet_with_form():
	headers = {
	    'Content-Type': 'application/x-www-form-urlencoded'
	}

	data = {
	  'name': 'update',
	  'status': 'pending'
	}

	response = requests.post('http://0.0.0.0:8080/pet/0', headers=headers, data=data)
	assert response.status_code == 200

def test_delete_pet():
	headers = {
	    'Content-Type': 'application/json',
	}

	valid_data = '{"category": {"id": 1, "name": "Mammal"}, "status": "available", "name": "doggie", "tags": [{"id": 1, "name": "doggie"}], "photoUrls": ["google.com"], "id": 1}'
	response = requests.post('http://0.0.0.0:8080/pet', headers=headers, data=valid_data) #Add a pet with ID 1
	assert response.status_code == 200
	
	response = requests.delete('http://0.0.0.0:8080/pet/1', headers=headers)
	assert response.status_code == 200


def test_upload_file():
	path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets/will.jpg')
	headers = {
	    'api_key': 'asdf1234567890',
	}

	files = {
	    'file': (path, open(path, 'rb')),
	}

	response = requests.post('http://0.0.0.0:8080/pet/0/uploadImage', headers=headers, files=files)

