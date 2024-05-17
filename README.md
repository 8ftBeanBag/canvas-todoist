# canvas-todoist by 8ftBeanBag

Forked from the awesome repo [Canvas-Assignments-Transfer-for-Todoist](https://github.com/scottquach/Canvas-Assignments-Transfer-For-Todoist) by [scottquach](https://github.com/scottquach)

***Not created by, affiliated with, or supported by Doist***

This script is designed specifically for the OMSCS SU2024 CS7638 class at Georgia Tech. I plan to update it as I go through the program to make it more flexible. 

This script imports
- Assignments
- Modules
- Quizzes

## The Basics

First, copy the `.env.example` file and rename your copy to .env.
```bash
cp .env.example .env
```

Next, install the dependencies
```bash
pip install -r requirements.txt
```

Fill it in with your keys and other info

> ### Canvas API Key
> On Canvas desktop go to settings and click on ```New Access Token``` under Approved Integrations

> ### Todoist API Key
> On Todoist desktop go to settings and the API token will be listed under the ```Integrations Tab```. You can also generate an application-specific token at https://developer.todoist.com/appconsole.html

Now just run the main file and watch your assignments, quizzes, and modules populate in associated sections.
```bash
python main.py
```

## Known Issues/Limitations
> :exclamation: Every teacher uses Canvas slightly differently. You agree that it is YOUR responsibility to review Canvas regularly to ensure you are staying current.


## Contributing & Troubleshooting
If you encounter any issues, please open an Issue with the appropriate data.

