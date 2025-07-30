from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from src.tools import AYXMCPTools


class MCPAlteryxServer:
    def __init__(self):
        """Initialize the MCP Alteryx Server"""
        self.tools = None
        self.app = None

    def initialize(self):
        """Initialize the server with tools and configuration"""
        # Load environment variables
        load_dotenv()

        # Initialize the AYXMCPTools instance
        self.tools = AYXMCPTools()

        # Initialize the setting for the FastMCP app
        # settings = {
        #     "debug": True,
        #     "log_level": "DEBUG",
        #     "host": "0.0.0.0",
        #     "port": 3001,
        # }
        # Initialize the FastMCP app
        self.app = FastMCP(
            name="mcp-alteryx-server",
            # settings=settings,
            prompt="""
# MCP Wrapper for Alteryx server

This MCP server provides tools for querying the remote Alteryx server using the Alteryx V3 API. It allows you to CRUD operations on Alteryx workflows, collections, users, jobs, connections and credendentials stored in the Alteryx server.

## Available Tools

### Collections
- get_all_collections: Get all collections
- get_collection_by_id: Get a specific collection
- create_collection: Create a new collection
- delete_collection: Delete a collection
- update_collection_name_or_owner: Update collection details
- add_workflow_to_collection: Add a workflow to a collection
- remove_workflow_from_collection: Remove a workflow from a collection
- add_schedule_to_collection: Add a schedule to a collection
- remove_schedule_from_collection: Remove a schedule from a collection

### Workflows
- get_all_workflows: Get all workflows
- get_workflow_by_id: Get a specific workflow
- update_workflow_name_or_comment: Update workflow details
- transfer_workflow: Transfer workflow ownership
- get_workflow_jobs: Get jobs for a workflow
- execute_workflow: Execute a workflow
- download_workflow_package_file: Download workflow package
- get_workflow_xml: Get workflow XML

### Users
- get_all_users: Get all users
- get_user_by_id: Get a specific user
- get_user_by_email: Get user by email
- get_user_by_name: Get user by name
- get_user_by_first_name: Get user by first name
- get_all_user_assets: Get all user assets
- get_user_assets_by_type: Get user assets by type
- update_user_details: Update user details
- transfer_all_assets: Transfer all user assets
- deactivate_user: Deactivate a user
- reset_user_password: Reset user password

### Jobs
- get_all_job_messages: Get all job messages
- get_job_by_id: Get a specific job

### Schedules
- get_all_schedules: Get all schedules
- get_schedule_by_id: Get a specific schedule
- deactivate_schedule: Deactivate a schedule
- activate_schedule: Activate a schedule
- update_schedule_name_or_comment: Update schedule details
- change_schedule_owner: Change schedule ownership

### Credentials and Connections
- get_all_credentials: Get all credentials
- get_credential_by_id: Get a specific credential
- lookup_connection: Lookup a connection
- get_connection_by_id: Get a specific connection

## Guidelines for Use

- Always check if a query would is about a workflow, a collection, a user, a job, a connection or a credential
- Keep queries concise and specific for best results
- Rate limits apply to all queries (typically 1 request/second)

## Output Format

All queries will be formatted as JSON for all results objects extracted from the Alteryx server.

- Workflow: Name, Description, and Created Date
- Collection: Name, Description, and Created Date
- User: Name, Email, and Created Date
- Job: Name, Description, and Created Date
- Connection: Name, Description, and Created Date
- Credential: Name, Description, and Created Date

If the API key is missing or invalid, appropriate error messages will be returned.
""",
        )
        return self

    def register_tools(self):
        """Register all tools with the MCP server"""
        if not self.app or not self.tools:
            raise RuntimeError("Server not initialized. Call initialize() first.")

        # Register Collections tools
        @self.app.tool()
        def get_all_collections():
            """Get the list of all collections of the Alteryx server"""
            return self.tools.get_all_collections()

        @self.app.tool()
        def get_collection_by_id(collection_id: str):
            """Get a collection by its ID"""
            return self.tools.get_collection_by_id(collection_id)

        @self.app.tool()
        def create_collection(name: str):
            """Create a new collection"""
            return self.tools.create_collection(name)

        @self.app.tool()
        def delete_collection(collection_id: str):
            """Delete a collection by its ID"""
            return self.tools.delete_collection(collection_id)

        @self.app.tool()
        def update_collection_name_or_owner(collection_id: str, name: str, owner_id: str):
            """Update a collection name or owner by its ID"""
            return self.tools.update_collection_name_or_owner(collection_id, name, owner_id)

        @self.app.tool()
        def add_workflow_to_collection(collection_id: str, workflow_id: str):
            """Add a workflow to a collection by its ID"""
            return self.tools.add_workflow_to_collection(collection_id, workflow_id)

        @self.app.tool()
        def remove_workflow_from_collection(collection_id: str, workflow_id: str):
            """Remove a workflow from a collection by its ID"""
            return self.tools.remove_workflow_from_collection(collection_id, workflow_id)

        @self.app.tool()
        def add_schedule_to_collection(collection_id: str, schedule_id: str):
            """Add a schedule to a collection by its ID"""
            return self.tools.add_schedule_to_collection(collection_id, schedule_id)

        @self.app.tool()
        def remove_schedule_from_collection(collection_id: str, schedule_id: str):
            """Remove a schedule from a collection by its ID"""
            return self.tools.remove_schedule_from_collection(collection_id, schedule_id)

        # Register Workflows tools
        @self.app.tool()
        def get_all_workflows():
            """Get the list of all workflows of the Alteryx server"""
            return self.tools.get_all_workflows()

        @self.app.tool()
        def get_workflow_by_id(workflow_id: str):
            """Get a workflow by its ID"""
            return self.tools.get_workflow_by_id(workflow_id)

        @self.app.tool()
        def update_workflow_name_or_comment(workflow_id: str, name: str, comment: str):
            """Update a workflow name or comment by its ID"""
            return self.tools.update_workflow_name_or_comment(workflow_id, name, comment)

        @self.app.tool()
        def download_workflow_package_file(workflow_id: str, output_directory: str):
            """Download a workflow package file by its ID and save it to the local directory"""
            return self.tools.download_workflow_package_file(workflow_id, output_directory)

        @self.app.tool()
        def get_workflow_xml(workflow_id: str):
            """Get the XML representation of a workflow file by its ID"""
            return self.tools.get_workflow_xml(workflow_id)

        @self.app.tool()
        def transfer_workflow(workflow_id: str, new_owner_id: str):
            """Transfer workflow ownership to a new user"""
            return self.tools.transfer_workflow(workflow_id, new_owner_id)

        @self.app.tool()
        def get_workflow_jobs(workflow_id: str):
            """Get all jobs associated with a workflow"""
            return self.tools.get_workflow_jobs(workflow_id)

        @self.app.tool()
        def execute_workflow(workflow_id: str):
            """Execute a workflow on the Alteryx server"""
            return self.tools.execute_workflow(workflow_id)

        # Register Users tools
        @self.app.tool()
        def get_all_users():
            """Get the list of all users of the Alteryx server"""
            return self.tools.get_all_users()

        @self.app.tool()
        def get_user_by_id(user_id: str):
            """Get a user by their ID"""
            return self.tools.get_user_by_id(user_id)

        @self.app.tool()
        def get_user_by_email(email: str):
            """Get a user by their email"""
            return self.tools.get_user_by_email(email)

        @self.app.tool()
        def get_user_by_name(name: str):
            """Get a user by their last name"""
            return self.tools.get_user_by_name(name)

        @self.app.tool()
        def get_user_by_first_name(first_name: str):
            """Get a user by their first name"""
            return self.tools.get_user_by_first_name(first_name)

        @self.app.tool()
        def get_all_user_assets(user_id: str):
            """Get all the assets for a user"""
            return self.tools.get_all_user_assets(user_id)

        @self.app.tool()
        def get_user_assets_by_type(user_id: str, asset_type: str):
            """Get user assets by type"""
            return self.tools.get_user_assets_by_type(user_id, asset_type)

        @self.app.tool()
        def update_user_details(user_id: str, first_name: str, last_name: str, email: str):
            """Update details of an existing user by their ID"""
            return self.tools.update_user_details(user_id, first_name, last_name, email)

        @self.app.tool()
        def transfer_all_assets(user_id: str, new_owner_id: str):
            """Transfer all assets from one user to another"""
            return self.tools.transfer_all_assets(user_id, new_owner_id)

        @self.app.tool()
        def deactivate_user(user_id: str):
            """Deactivate a user account"""
            return self.tools.deactivate_user(user_id)

        @self.app.tool()
        def reset_user_password(user_id: str):
            """Reset a user's password by their ID"""
            return self.tools.reset_user_password(user_id)

        # Register Jobs tools
        @self.app.tool()
        def get_all_job_messages(job_id: str):
            """Get all the messages for a job"""
            return self.tools.get_all_job_messages(job_id)

        @self.app.tool()
        def get_job_by_id(job_id: str):
            """Retrieve details about an existing job and its current state"""
            return self.tools.get_job_by_id(job_id)

        # Register Schedules tools
        @self.app.tool()
        def get_all_schedules():
            """Get the list of all schedules of the Alteryx server"""
            return self.tools.get_all_schedules()

        @self.app.tool()
        def get_schedule_by_id(schedule_id: str):
            """Get a schedule by its ID"""
            return self.tools.get_schedule_by_id(schedule_id)

        @self.app.tool()
        def deactivate_schedule(schedule_id: str):
            """Deactivate a schedule by its ID"""
            return self.tools.deactivate_schedule(schedule_id)

        @self.app.tool()
        def activate_schedule(schedule_id: str):
            """Activate a schedule by its ID"""
            return self.tools.activate_schedule(schedule_id)

        @self.app.tool()
        def update_schedule_name_or_comment(schedule_id: str, name: str, comment: str):
            """Update a schedule name or comment by its ID"""
            return self.tools.update_schedule_name_or_comment(schedule_id, name, comment)

        @self.app.tool()
        def change_schedule_owner(schedule_id: str, new_owner_id: str):
            """Change the owner of a schedule by its ID"""
            return self.tools.change_schedule_owner(schedule_id, new_owner_id)

        # Register Credentials tools
        @self.app.tool()
        def get_all_credentials():
            """Get the list of all accessible credentials of the Alteryx server"""
            return self.tools.get_all_credentials()

        @self.app.tool()
        def get_credential_by_id(credential_id: str):
            """Get the details of an existing credential"""
            return self.tools.get_credential_by_id(credential_id)

        # Register Connections tools
        @self.app.tool()
        def lookup_connection(connection_id: str):
            """Lookup a DCM Connection as referenced in workflows"""
            return self.tools.lookup_connection(connection_id)

        @self.app.tool()
        def get_connection_by_id(connection_id: str):
            """Get a connection by its ID"""
            return self.tools.get_connection_by_id(connection_id)

        return self
