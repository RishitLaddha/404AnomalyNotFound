from locust import HttpUser, task, between

class DVWAUser(HttpUser):
    host = "http://localhost:9001"
    wait_time = between(1, 3)

    @task(3)
    def home(self):
        self.client.get("/")

    @task(2)
    def login_page(self):
        self.client.get("/login.php")
