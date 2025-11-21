import os
import requests
from calcure.data import Task, Status, Timer

class LiveLoader:
    """Base class for live data connectors"""
    def load(self):
        raise NotImplementedError

class NotionTaskLoader(LiveLoader):
    """Load tasks from Notion Database"""
    def __init__(self, cf):
        self.token = os.environ.get("NOTION_TOKEN")
        self.database_id = os.environ.get("NOTION_DATABASE_ID")
        self.target_person_id = None
        self.user_name_query = "Ethan Hitchcock" # User to filter by
        self.status_options = []
        self.project_cache = {}  # Cache project IDs to names

    def fetch_status_options(self, headers):
        """Fetch available status options from the database schema"""
        url = f"https://api.notion.com/v1/databases/{self.database_id}"
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                status_prop = data.get("properties", {}).get("Status", {})
                # Handle 'status' type property
                if status_prop.get("type") == "status":
                    status_config = status_prop.get("status", {})
                    options = status_config.get("options", [])
                    # Extract option names
                    self.status_options = [{"name": opt.get("name"), "id": opt.get("id")} for opt in options]
                # Handle 'select' type property if used for status
                elif status_prop.get("type") == "select":
                    select_config = status_prop.get("select", {})
                    options = select_config.get("options", [])
                    self.status_options = [{"name": opt.get("name"), "id": opt.get("id")} for opt in options]
        except Exception:
            pass

    def fetch_project_name(self, project_id, headers):
        """Fetch project name from Notion page"""
        if project_id == "No Project":
            return "No Project"
        
        # Check cache first
        if project_id in self.project_cache:
            return self.project_cache[project_id]
        
        try:
            url = f"https://api.notion.com/v1/pages/{project_id}"
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                # Get title from properties - try common title property names
                props = data.get("properties", {})
                
                # Try "Name" first (most common)
                if "Name" in props:
                    title_prop = props["Name"].get("title", [])
                    if title_prop:
                        project_name = title_prop[0].get("plain_text", project_id)
                        self.project_cache[project_id] = project_name
                        return project_name
                
                # Try "Title"
                if "Title" in props:
                    title_prop = props["Title"].get("title", [])
                    if title_prop:
                        project_name = title_prop[0].get("plain_text", project_id)
                        self.project_cache[project_id] = project_name
                        return project_name
                
                # Try any property with "title" type
                for prop_name, prop_data in props.items():
                    if prop_data.get("type") == "title":
                        title_prop = prop_data.get("title", [])
                        if title_prop:
                            project_name = title_prop[0].get("plain_text", project_id)
                            self.project_cache[project_id] = project_name
                            return project_name
                
                # Fallback: use page ID if no title found
                self.project_cache[project_id] = project_id
                return project_id
        except Exception:
            pass
        
        # Fallback to ID if fetch fails
        self.project_cache[project_id] = project_id
        return project_id

    def load(self):
        if not self.token or not self.database_id:
            return []
            
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        
        # Fetch status options first
        self.fetch_status_options(headers)

        payload = {
            "filter": {
                "and": [
                    {
                        "property": "Status",
                        "status": {
                            "does_not_equal": "Done"
                        }
                    },
                    {
                        "property": "Status",
                        "status": {
                            "does_not_equal": "Completed"
                        }
                    }
                ]
            },
            "sorts": [
                {
                    "property": "Project",
                    "direction": "ascending"
                }
            ]
        }

        url = f"https://api.notion.com/v1/databases/{self.database_id}/query"
        
        try:
            response = requests.post(url, headers=headers, json=payload)
        except Exception:
            return []
        
        tasks = []
        if response.status_code == 200:
            data = response.json()
            
            current_project_id = None
            
            for result in data.get("results", []):
                props = result.get("properties", {})
                
                # 1. Filter by Responsible Person
                responsible_list = props.get("Responsible", {}).get("people", [])
                is_responsible = False
                for person in responsible_list:
                    if person.get("name") == self.user_name_query:
                        is_responsible = True
                        break
                
                if not is_responsible:
                    continue

                # 2. Get Task Info
                task_name = "Untitled Task"
                title_prop = props.get("Task name", {}).get("title", [])
                if title_prop:
                    task_name = title_prop[0].get("plain_text", "Untitled Task")

                notion_id = result.get("id")
                
                # 3. Project Grouping - fetch project name
                project_rels = props.get("Project", {}).get("relation", [])
                project_id = project_rels[0].get("id") if project_rels else "No Project"
                project_name = self.fetch_project_name(project_id, headers)
                
                # Insert Header if project changed
                if project_id != current_project_id:
                    current_project_id = project_id
                    # Create a Header Task with actual project name
                    header_task = Task(0, project_name, Status.NORMAL, Timer([]), False, 
                                     project_name=project_name, is_header=True)
                    tasks.append(header_task)

                # Status
                status_obj = props.get("Status", {}).get("status", {})
                status_name = status_obj.get("name")
                calcure_status = Status.NORMAL
                if status_name in ["High", "Urgent"]:
                    calcure_status = Status.IMPORTANT
                
                task = Task(0, task_name, calcure_status, Timer([]), False, 
                            notion_id=notion_id, 
                            project_name=project_name, 
                            notion_status_options=self.status_options,
                            current_notion_status=status_name)
                tasks.append(task)
                
        return tasks

class NotionTaskSaver:
    """Save updates back to Notion"""
    def __init__(self):
        self.token = os.environ.get("NOTION_TOKEN")

    def update_status(self, task_id, new_status_name):
        """Update the status of a task in Notion"""
        if not self.token or not task_id:
            return

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        
        url = f"https://api.notion.com/v1/pages/{task_id}"
        
        payload = {
            "properties": {
                "Status": {
                    "status": {
                        "name": new_status_name
                    }
                }
            }
        }
        
        try:
            requests.patch(url, headers=headers, json=payload)
        except Exception:
            pass

class MSTodoLoader(LiveLoader):
    """Load tasks from Microsoft To Do"""
    def __init__(self, cf):
        pass
