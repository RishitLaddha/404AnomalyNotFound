from locust import HttpUser, task, between

class JuiceShopUser(HttpUser):
    wait_time = between(1, 5)

    @task(3)
    def browse_home(self):
        self.client.get("/")

    @task(2)
    def socket_poll(self):
        self.client.get("/socket.io/?EIO=4&transport=polling")

