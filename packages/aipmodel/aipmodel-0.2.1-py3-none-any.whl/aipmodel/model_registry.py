import requests
import base64

class ModelRegistry:
    def __init__(self, endpoint_url: str, access_key: str, secret_key: str, user_name: str):
        self.endpoint_url = endpoint_url.rstrip('/')
        encoded = base64.b64encode(f"{access_key}:{secret_key}".encode()).decode()
        res = requests.post(
            f"{self.endpoint_url}/auth.login",
            headers={'Authorization': f'Basic {encoded}'}
        )
        res.raise_for_status()
        self.token = res.json()['data']['token']
        self.user_name = user_name
        self.project_id = None

    def _headers(self):
        return {'Authorization': f'Bearer {self.token}'}

    def get_projects(self):
        res = requests.post(f"{self.endpoint_url}/projects.get_all", headers=self._headers())
        res.raise_for_status()
        return res.json()['data']['projects']

    def get_project(self):
        name = f"model_registry_{self.user_name}"
        projects = self.get_projects()
        for project in projects:
            if project['name'] == name:
                self.project_id = project['id']
                return project
        return None

    def create_project(self):
        if self.get_project():
            return self.project_id
        name = f"model_registry_{self.user_name}"
        res = requests.post(
            f"{self.endpoint_url}/projects.create",
            headers=self._headers(),
            json={'name': name, 'description': f'Model registry for {self.user_name}'}
        )
        res.raise_for_status()
        self.project_id = res.json()['data']['id']
        return self.project_id

    def delete_project(self):
        project = self.get_project()
        if not project:
            return None
        res = requests.post(
            f"{self.endpoint_url}/projects.delete",
            headers=self._headers(),
            json={'project': self.project_id, 'delete_contents': True}
        )
        res.raise_for_status()
        return self.project_id

    def get_models(self, name=None):
        self.create_project()
        payload = {'project': self.project_id}
        if name:
            payload['name'] = name
        res = requests.post(
            f"{self.endpoint_url}/models.get_all",
            headers=self._headers(),
            json=payload
        )
        res.raise_for_status()
        return res.json()['data']['models']

    def add_model(self, name: str, uri: str):
        self.create_project()
        payload = {
            'project': self.project_id,
            'name': name,
            'uri': uri
        }
        res = requests.post(
            f"{self.endpoint_url}/models.create",
            headers=self._headers(),
            json=payload
        )
        res.raise_for_status()
        return res.json()['data']['id']

    def delete_models(self, name: str):
        deleted = []
        for model in self.get_models(name):
            res = requests.post(
                f"{self.endpoint_url}/models.delete",
                headers=self._headers(),
                json={'model': model['id']}
            )
            res.raise_for_status()
            if res.json()['data'].get('deleted'):
                deleted.append(model['id'])
        return deleted


if __name__ == '__main__':
    model_registry = ModelRegistry(
        endpoint_url="http://213.233.184.112:30008",
        access_key="WNPZX135R8ZVVG7U9FMAMSXCAS6EUP",
        secret_key="eESDKoxmWqE_f5ODs2nSKGoFqgAcdSSf5ixoeDQETByV5BhMzWpQ0OhmUri0f77XeqY",
        user_name="mohammad"
    )

    # Print out the access token first (for debugging)
    print(f"Token: {model_registry.token[:20]}...")

    # Create or get the existing project
    project_id = model_registry.create_project()
    print(f"\nCreated or existing project ID: {project_id}")
    
    # Print all projects available
    print("\nAll Projects:")
    projects = model_registry.get_projects()
    for project in projects:
        print(f"- {project['id']} | {project['name']}")
        
    # Fetch and print project info
    project_info = model_registry.get_project()
    print("Project info:")
    if project_info:
        print(f"  Name: {project_info['name']}")
        print(f"  ID: {project_info['id']}")
        print(f"  Description: {project_info['description']}")
    else:
        print("No project found.")

    # Add a model to the registry
    model_id = model_registry.add_model(
        name="whisper",
        uri="s3://almmlops/models/whisper/whisper-large-v2-fa"
    )
    print(f"\nCreated model ID: {model_id}")

    # List models by name
    models = model_registry.get_models(name="DevOps")
    print("Found models:")
    for m in models:
        print(f"- {m['id']} | {m['name']}")

    # Delete models by name
    # deleted = model_registry.delete_models(name="whisper")
    # print(f"Deleted model IDs: {deleted}")

    # Delete the project
    # deleted_project = model_registry.delete_project()
    # print(f"Deleted project ID: {deleted_project}")
