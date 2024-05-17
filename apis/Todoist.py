import time
from todoist_api_python.api import TodoistAPI

class LimitReachedError(Exception):
    def __init__(self, message):            
        super().__init__(message)
        print("Error while adding task. Likely due to rate limiting. Try again in 15 minutes", message)

class Todoist:
    api = None
    limit_reached = False
    request_count = 0
    throttle_number = 50
    sleep_delay_max = 1
    
    def __init__(self, config):
        self.api = TodoistAPI(config["TODOIST_TOKEN"].strip())
        self.sleep_delay_max = int(config["API_LIMIT"]) if "API_LIMIT" in config else 1
        
    # Throttle requests to Todoist API to prevent rate limiting, sleep every 50 requests
    def throttle(self):
        if self.request_count % self.throttle_number == 0 and self.request_count > 1:
            time.sleep(self.sleep_delay_max)
        self.request_count += 1
        
    # Loads all user tasks from Todoist
    def get_tasks(self):
        self.throttle()
        return self.api.get_tasks()

    # Loads all user projects from Todoist
    def get_projects(self):
        self.throttle()
        return self.api.get_projects() 
    
    def create_or_get_sections(self, section_names, project_id):
        self.throttle()
        cur_sections = self.api.get_sections()
        cur_section_names_in_project = list(map(
            lambda s: s.name, 
            [cs for cs in cur_sections if cs.project_id == project_id]
        ))
        
        sections = {}
        for name in section_names:
            if name in cur_section_names_in_project:
                sections[name] = next(cs for cs in cur_sections if cs.name == name)
            else:
                sections[name] = self.create_section(name, project_id)
        return sections
            
    def create_section(self, section_name, project_id):
        self.throttle()
        return self.api.add_section(section_name, project_id)
        
    # Adds a new task from a Canvas assignment object to Todoist under the
    # project corresponding to project_id
    def add_canvas_assignment_as_task(self, canvas_assignment, project_id, section, priority=1):
        self.throttle()
        if self.limit_reached:
            raise LimitReachedError
        try:
            # Initialize content
            content = f"{canvas_assignment.name} [ID: {canvas_assignment.id}]"
            
            # Build labels list
            labels = [
                canvas_assignment.submission_types,
            ]
            if canvas_assignment.due_at is None:
                labels.append("no due date")
                
            if canvas_assignment.unlock_at is not None:
                labels.append("locked")
                content += f" unlocks on {canvas_assignment.unlock_at}"
            
            if canvas_assignment.locked_for_user and canvas_assignment.unlock_at is None:
                labels.append("no access")
                
            self.api.add_task(
                content = content,
                project_id=project_id,
                due_datetime=canvas_assignment.due_at,
                labels=labels,
                priority=priority,
                section_id=section,
                description=f"{canvas_assignment.html_url}\n{canvas_assignment.description}"
            )
        except Exception:
            self.limit_reached = True
            raise LimitReachedError
        
    # Adds a new task from a Canvas module object to Todoist under the
    # project corresponding to project_id
    def add_canvas_module_as_task(self, canvas_module, project_id, section, priority=1):
        self.throttle()
        if self.limit_reached:
            raise LimitReachedError
        try:
            # Initialize content
            content = f"{canvas_module.name} [ID: {canvas_module.id}]"
            labels = []
            
            if canvas_module.unlock_at is not None:
                labels = ["locked"]
                content += f" unlocks on {canvas_module.unlock_at}"
                
            self.api.add_task(
                content = content,
                project_id=project_id,
                labels=labels,
                priority=priority,
                section_id=section,
                description=f"{canvas_module.items_url}\n \
                    Number of Items: {canvas_module.items_count}"
            )
        except Exception:
            self.limit_reached = True
            raise LimitReachedError
        
    # Adds a new task from a Canvas quiz object to Todoist under the
    # project corresponding to project_id
    def add_canvas_quiz_as_task(self, canvas_quiz, project_id, section, priority=1):
        self.throttle()
        if self.limit_reached:
            raise LimitReachedError
        try:
            # Initialize content
            content = f"{canvas_quiz.name} [ID: {canvas_quiz.id}]"
            
            # Build labels list
            labels = [canvas_quiz.quiz_type]
            if canvas_quiz.due_at is None:
                labels.append("no due date")
                
            if canvas_quiz.unlock_at is not None:
                labels.append("locked")
                content += f" unlocks on {canvas_quiz.unlock_at}"
            
            if canvas_quiz.locked_for_user and canvas_quiz.unlock_at is None:
                labels.append("no access")
                
            self.api.add_task(
                content = content,
                project_id=project_id,
                due_datetime=canvas_quiz.due_at,
                labels=labels,
                priority=priority,
                section_id=section,
                description=f"\
                    {canvas_quiz.html_url}\n \
                    {canvas_quiz.description}\n \
                    Allowed attempts: {canvas_quiz.allowed_attempts}\n \
                    Points possible: {canvas_quiz.points_possible}"
            )
        except Exception:
            self.limit_reached = True
            raise LimitReachedError