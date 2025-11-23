import logging
import random
import uuid

from locust import HttpUser, between, task


class PRServiceUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """
        Инициализация перед началом тестов для каждого виртуального пользователя.
        """
        self.team_name = f"team_{uuid.uuid4().hex[:8]}"
        self.author_id = f"user_{uuid.uuid4().hex[:8]}"
        self.active_prs = []

        self.team_members = []
        members_payload = [{"user_id": self.author_id, "username": "Author_Lead", "is_active": True}]

        for i in range(5):
            uid = f"user_{uuid.uuid4().hex[:8]}"
            self.team_members.append(uid)
            members_payload.append({"user_id": uid, "username": f"Dev_{i}", "is_active": True})

        payload = {"team_name": self.team_name, "members": members_payload}

        with self.client.post("/team/add", json=payload, catch_response=True) as response:
            if response.status_code != 201:
                logging.error(f"Failed to create team: {response.text}")
                response.failure("Setup failed: Could not create team")

    @task(3)
    def create_pull_request(self):
        """
        Создание PR (частое действие)
        """
        pr_id = f"PR-Feature-{uuid.uuid4().hex[:8]}"
        pr_name = f"PR-Feature-{uuid.uuid4().hex[:3]}"
        payload = {"pull_request_id": pr_id, "pull_request_name": pr_name, "author_id": self.author_id}

        with self.client.post("/pullRequest/create", json=payload, catch_response=True) as response:
            if response.status_code == 201:
                data = response.json()

                if "pr" in data:
                    pr_obj = data["pr"]
                    self.active_prs.append(
                        {"id": pr_obj["pull_request_id"], "reviewers": pr_obj.get("assigned_reviewers", [])}
                    )
                else:
                    logging.error(f"Unexpected response structure: {data}")
            elif response.status_code == 409:
                response.success()
            else:
                response.failure(f"Create PR failed: {response.status_code}")

    @task(5)
    def get_team_info(self):
        """
        Получение информации о команде. Самая частая операция (чтение)
        """
        self.client.get(f"/team/get?team_name={self.team_name}", name="/team/get")

    @task(4)
    def get_user_reviews(self):
        """
        Просмотр списка ревью пользователя
        """

        target_user = random.choice(self.team_members + [self.author_id])
        self.client.get(f"/users/getReview?user_id={target_user}", name="/users/getReview")

    @task(2)
    def reassign_reviewer(self):
        """
        Переназначение ревьювера
        """
        if not self.active_prs:
            return

        pr_data = random.choice(self.active_prs)
        pr_id = pr_data["id"]
        current_reviewers = pr_data["reviewers"]

        if not current_reviewers:
            return

        old_reviewer_id = random.choice(current_reviewers)

        payload = {"pull_request_id": pr_id, "old_user_id": old_reviewer_id}

        with self.client.post("/pullRequest/reassign", json=payload, catch_response=True) as response:
            if response.status_code == 200:
                try:
                    resp_data = response.json()
                    new_reviewer_id = resp_data.get("replaced_by")

                    if new_reviewer_id:
                        if old_reviewer_id in current_reviewers:
                            current_reviewers.remove(old_reviewer_id)
                        current_reviewers.append(new_reviewer_id)

                except Exception as e:
                    logging.error(f"Error parsing reassign response: {e}")

            elif response.status_code == 404:
                if pr_data in self.active_prs:
                    self.active_prs.remove(pr_data)
                response.failure("Reassign failed: PR not found")
            elif response.status_code == 409:
                response.success()

    @task(1)
    def merge_pull_request(self):
        """
        Мердж PR (редкое действие, завершает цикл).
        """
        if not self.active_prs:
            return

        pr_data = random.choice(self.active_prs)
        pr_id = pr_data["id"]

        payload = {"pull_request_id": pr_id}

        with self.client.post("/pullRequest/merge", json=payload, catch_response=True) as response:
            if response.status_code == 200:
                self.active_prs.remove(pr_data)
            elif response.status_code == 404:
                if pr_data in self.active_prs:
                    self.active_prs.remove(pr_data)
                response.failure("Merge failed: PR not found")
