from locust import HttpUser, task, between

class DVWAUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def browse_home(self):
        self.client.get("/")

    @task(2)
    def login_page(self):
        self.client.get("/login.php")


class JuiceShopUser(HttpUser):
    wait_time = between(1, 5)

    @task(3)
    def browse_products(self):
        self.client.get("/")

    @task(2)
    def socket_poll(self):
        self.client.get("/socket.io/?EIO=4&transport=polling")


class WebGoatUser(HttpUser):
    wait_time = between(2, 6)

    @task
    def browse_webgoat(self):
        self.client.get("/WebGoat")

