from locust import HttpUser, task, between


item_path = "/api/v1/item/"
staff_path = "/api/v1/staff/"

token_path = "/auth/login/"
revoke_path = "/auth/revoke/"

admin_token_form = {
    "username": "admin",
    "password": "admin",
}



import secrets

class StressTestBackend(HttpUser):
    host = "http://localhost:8000"
    wait_time = between(1, 5)

    @task(2)
    def stress_item_lifecycle(self):
        
        max_len=10
        id=secrets.token_hex(max_len // 2)

        name = f"test: {id}"
        json_data = {
            "name": name,
            "description": "test",
            "tags": ["test"],
            "price": 10,
            "tax": 0,
        }
        

        with self.client.post(
            item_path,
            json=json_data,
            headers=self.auth_header,
            catch_response=True,
        ) as response:
            if response.status_code != 201:
                response.failure(f"Problem at POST: {response.text}")
        
        response = self.client.get(
            item_path,
            params={"name": name},
        )

        response = self.client.delete(
            item_path,
            params={"name": name},
            headers=self.auth_header,
        )

    """
    Not yet implemented, since the route to get the key is cumbersome


    @task(2)
    def stres_staff_lifecycle(self):
        
        max_len=10
        id=secrets.token_hex(max_len // 2)

        name = f"test: {id}"
        json_data = {
            "name": name,
            "age": 18,
            "monthly_wage": 0,
            "role": "staff",
        }
        

        with self.client.post(
            staffpath,
            json=json_data,
            headers=self.auth_header,
            catch_response=True,
        ) as response:
            if response.status_code != 201:
                response.failure(f"Problem at POST: {response.text}")
        
        response = self.client.get(
            staff_path,
            params={"name": name},
        )

        response = self.client.delete(
            staff_path,
            params={"name": name},
            headers=self.auth_header,
        )
    """

    @task
    def stress_staff_get_seeded(self):
        params = {
            "name": "test",
        }
        response = self.client.get(staff_path, params=params)
 
 
    @task
    def stress_item_get_seeded(self):

        params = {
            "name": "test",
        }
        response = self.client.get(item_path, params=params)
      

    def on_start(self):
        response = self.client.post(token_path, data=admin_token_form)
        if response.status_code == 200:
            self.auth_header = {"Authorization": f"Bearer {response.json().get("access_token")}"}
        else:
            self.auth_header = None

