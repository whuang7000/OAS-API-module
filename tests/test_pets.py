import requests

def test_update_pet():
	headers = {
	    'Content-Type': 'application/json',
	}

	valid_data = '{"category": {"id": 0, "name": "Mammal"}, "status": "available", "name": "doggie", "tags": [{"id": 0, "name": "doggie"}], "photoUrls": ["google.com"], "id": 0}'
	response = requests.put('http://0.0.0.0:8080/pet', headers=headers, data=valid_data)
	assert response.status_code == 200

	invalid_data = '{"category": {"id": 0, "name": "Mammal"}, "status": "available", "name": "doggie", "tags": [{"id": 0, "name": "doggie"}], "photoUrls": ["google.com"], "id": 0.5}'
	response = requests.put('http://0.0.0.0:8080/pet', headers=headers, data=invalid_data)
	assert response.status_code == 400 #Validation error

def test_add_pet():
	headers = {
	    'Content-Type': 'application/json',
	}

	valid_data = '{"category": {"id": 0, "name": "Mammal"}, "status": "available", "name": "doggie", "tags": [{"id": 0, "name": "doggie"}], "photoUrls": ["google.com"], "id": 0}'
	response = requests.post('http://0.0.0.0:8080/pet', headers=headers, data=valid_data)
	assert response.status_code == 200

	invalid_data = '{"category": {"id": 0, "name": "Mammal"}, "status": "available", "name": "doggie", "tags": [{"id": 0, "name": "doggie"}], "photoUrls": ["google.com"], "id": 0.5}'
	response = requests.post('http://0.0.0.0:8080/pet', headers=headers, data=invalid_data)
	assert response.status_code == 400 #Validation Error because id is a decimal

def test_find_pets_by_status():
	valid_params = [
    	('status', 'pending'),
	]

	response = requests.get('http://0.0.0.0:8080/pet/findByStatus', params=valid_params)
	assert response.status_code == 200

	invalid_params = [
		('status', 'onhold') 
	]
	response = requests.get('http://0.0.0.0:8080/pet/findByStatus', params=invalid_params)
	assert response.status_code == 400 #Status doesn't exist

def test_find_pets_by_tags():
	valid_params = [
    	('tags', ['doggie','cat'])
	]

	response = requests.get('http://0.0.0.0:8080/pet/findByTags', params=valid_params)
	assert response.status_code == 200





