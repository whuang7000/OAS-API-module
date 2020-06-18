import requests

def test_get_inventory():
	response = requests.get('http://0.0.0.0:8080/store/inventory')
	assert response.status_code == 200

def test_place_order():
	headers = {
	    'Content-Type': 'application/json'
	}

	valid_data = '{"id": 1,"petId": 0}'

	response = requests.post('http://0.0.0.0:8080/store/order', headers=headers, data=valid_data)
	assert response.status_code == 200

	invalid_data = '{"id": "string","petId": 0}'

	response = requests.post('http://0.0.0.0:8080/store/order', headers=headers, data=invalid_data)
	assert response.status_code == 400 #Invalid order ID

def test_get_order_by_id():
	response = requests.get('http://0.0.0.0:8080/store/order/1')
	assert response.status_code == 200

def test_delete_order():	
	response = requests.delete('http://0.0.0.0:8080/store/order/2')
	assert response.status_code == 200
