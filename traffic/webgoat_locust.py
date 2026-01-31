from locust import HttpUser, task, between

class WebGoatUser(HttpUser):
    wait_time = between(2, 6)

    @task
    def browse_webgoat(self):
        self.client.get("/WebGoat")

