from locust import HttpUser, task

#Still not ready

class StressTestBackend(HttpUser):
    @task
    def hello_world(self):
        self.client.get("/hello")
        self.client.get("/world")
