# -*- coding: utf-8 -*-
# Import Libraries
from dotenv import load_dotenv, dotenv_values
import inquirer
from Canvas import Canvas
from Todoist import Todoist
import re
from alive_progress import alive_bar

# Load configuration files and creates a list of course_ids
load_dotenv()

def main():
    # Setup
    config = dotenv_values(".env")
    canvas_api = Canvas(config)
    todoist_api = Todoist(config)

    # Get the project to add the tasks to
    todoist_projects = todoist_api.get_projects()
    project = get_project_from_user(todoist_projects) \
              if config["PROJECT_NAME"] is None \
              else next(tp.id for tp in todoist_projects if tp.name == config["PROJECT_NAME"])
    
    # get all tasks and map them to canvas ids
    current_tasks = todoist_api.get_tasks()
    current_task_canvas_ids = [
        int(re.search(r'\[ID:(.*?)\]', ct.content).group(1))
        for ct in current_tasks 
        if ct.content.find("[ID:") != -1
    ]
    
    # Create or get the sections
    sections = todoist_api.create_or_get_sections(["Assignments", "Modules", "Quizzes"], project)
        
    # Get the assignments
    print("Adding Assignments")
    assignments = canvas_api.get_course_assignments(config["COURSE_ID"])
    with alive_bar(len(assignments)) as bar:
        for assignment in assignments:
            if assignment.id not in current_task_canvas_ids:
                todoist_api.add_canvas_assignment_as_task(assignment, project, sections["Assignments"].id)
                bar()
            else: bar(skipped=True)
      
    # Get the quizzes
    print("Adding Quizzes")
    quizzes = canvas_api.get_course_quizzes(config["COURSE_ID"])
    with alive_bar(len(quizzes)) as bar:
        for quiz in quizzes:
            if quiz.id not in current_task_canvas_ids:
                todoist_api.add_canvas_quiz_as_task(quiz, project, sections["Quizzes"].id)
                bar()
            else: bar(skipped=True)
            
    # Get the modules
    print("Adding Modules")
    modules = canvas_api.get_course_modules(config["COURSE_ID"])
    with alive_bar(len(modules)) as bar:
        for module in modules:
            if module.id not in current_task_canvas_ids:
                todoist_api.add_canvas_module_as_task(module, project, sections["Modules"].id)
                bar()
            else: bar(skipped=True)
    print("Done!")
    
def get_project_from_user(projects):
    questions = [
        inquirer.List(
            'project',
            message="What project do you want to add the tasks to?",
            choices=list(map(lambda p: p.name, projects)),
        ),
    ]
    answers = inquirer.prompt(questions)
    return next(p.id for p in projects if p.name == answers["project"])
    
if __name__=="__main__":
    main()