import requests
import re
import time

class UnauthorizedError(Exception):
    def __init__(self, message):            
        super().__init__(message)
        print("Canvas Unauthorized; Check API Key", message)

class CanvasAssignment:
    def __init__(self, json):
        self.id = json["id"]
        self.name = json["name"]
        self.description = json["description"]
        self.due_at = json["due_at"]
        self.lock_at = json["lock_at"]
        self.unlock_at = json["unlock_at"]
        self.html_url = json["html_url"]
        self.points_possible = json["points_possible"]
        self.allowed_attempts = json["allowed_attempts"]
        self.submission_types = json["submission_types"][0]
        self.locked_for_user = json["locked_for_user"]
        
class CanvasQuiz:
    def __init__(self, json):
        self.id = json["id"]
        self.html_url = json["html_url"]
        self.name = json["title"]
        self.description = json["description"]
        self.quiz_type = json["quiz_type"]
        self.allowed_attempts = json["allowed_attempts"] if json["allowed_attempts"] != -1 else "Unknown"
        self.points_possible = json["points_possible"]
        self.due_at = json["due_at"]
        self.lock_at = json["lock_at"]
        self.unlock_at = json["unlock_at"]
        self.locked_for_user = json["locked_for_user"]
        
class CanvasModule:
    def __init__(self, json):
        self.id = json["id"]
        self.name = json["name"]
        self.unlock_at = json["unlock_at"]
        self.items_count = json["items_count"]
        self.items_url = json["items_url"]
    
class Canvas:
    header = {}
    api_path = ""
    params = {"per_page": "100", "include": "submission", "enrollment_state": "active"}
    sleep_delay_max = 1

    def __init__(self, config):
        self.header.update({"Authorization": f"Bearer {config['CANVAS_TOKEN'].strip()}"})
        self.api_path = f"{config['CANVAS_API']}/api/v1/courses"
        self.sleep_delay_max = int(config["API_LIMIT"]) if "API_LIMIT" in config else 1

    def get_api(self, local_url=""):
        response = requests.get(
            f"{self.api_path}/{local_url}",
            headers=self.header,
            params=self.params,
        )
        if response.status_code == 401:
            raise UnauthorizedError
        return response

    def get_paginated_results(self, local_url):
        response = self.get_api(local_url)
        paginated = response.json()

        while "next" in response.links:
            time.sleep(self.sleep_delay_max)    
            response = self.get_api(response.links["next"]["url"])
            paginated.extend(response.json())
        return paginated
        
    def get_course_assignments(self, course):
        assignments = self.get_paginated_results(f"{course}/assignments")
        return list(map(lambda a: CanvasAssignment(a), assignments))

    def get_course_modules(self, course):
        modules = self.get_paginated_results(f"{course}/modules")
        return list(map(lambda a: CanvasModule(a), modules))
    
    def get_course_quizzes(self, course):
        quizzes = self.get_paginated_results(f"{course}/quizzes")
        return list(map(lambda a: CanvasQuiz(a), quizzes))