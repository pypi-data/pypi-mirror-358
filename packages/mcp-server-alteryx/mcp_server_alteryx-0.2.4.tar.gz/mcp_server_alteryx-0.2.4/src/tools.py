import src.server_client as server_client
from src.server_client.rest import ApiException
import pprint
import tempfile
import zipfile
import os
import shutil
from pydantic import BaseModel


class InputData(BaseModel):
    name: str
    value: str


class AYXMCPTools:
    def __init__(self):
        """Initialize the Alteryx Server Client with API instances"""
        self.configuration = server_client.Configuration()
        self.collections_api = server_client.CollectionsApi(server_client.ApiClient(self.configuration))
        self.workflows_api = server_client.WorkflowsApi(server_client.ApiClient(self.configuration))
        self.users_api = server_client.UsersApi(server_client.ApiClient(self.configuration))
        self.jobs_api = server_client.JobsApi(server_client.ApiClient(self.configuration))
        self.credentials_api = server_client.CredentialsApi(server_client.ApiClient(self.configuration))
        self.dcm_api = server_client.DCMEApi(server_client.ApiClient(self.configuration))
        self.schedules_api = server_client.SchedulesApi(server_client.ApiClient(self.configuration))

    # Collections functions
    def get_all_collections(self):
        """Get the list of all collections of the Alteryx server"""
        try:
            api_response = self.collections_api.collections_get_collections()
            return pprint.pformat(api_response)
        except ApiException as e:
            return f"Error: {e}"

    def get_collection_by_id(self, collection_id: str):
        """Get a collection by its ID"""
        try:
            api_response = self.collections_api.collections_get_collection(collection_id)
            return pprint.pformat(api_response)
        except ApiException as e:
            return f"Error: {e}"

    def create_collection(self, name: str):
        """Create a new collection. To add a collection to a user, use the update_collection_name_or_owner function."""
        try:
            contract = server_client.CreateCollectionContract(name=name)
            api_response = self.collections_api.collections_create_collection(contract)
            return pprint.pformat(api_response)
        except ApiException as e:
            return f"Error: {e}"

    def delete_collection(self, collection_id: str):
        """Delete a collection by its ID"""
        try:
            collection = self.collections_api.collections_get_collection(collection_id)
            if not collection:
                return "Error: Collection not found"
            api_response = self.collections_api.collections_delete_collection(collection_id)
            return pprint.pformat(api_response)
        except ApiException as e:
            return f"Error: {e}"

    def update_collection_name_or_owner(self, collection_id: str, name: str, owner_id: str):
        """Update a collection name or owner by its ID"""
        try:
            collection = self.collections_api.collections_get_collection(collection_id)
            if not collection:
                return "Error: Collection not found"
            contract = server_client.UpdateCollectionContract(
                name=name if name else collection.name, owner_id=owner_id if owner_id else collection.owner_id
            )
            api_response = self.collections_api.collections_update_collection(collection_id, contract)
            return pprint.pformat(api_response)
        except ApiException as e:
            return f"Error: {e}"

    def add_workflow_to_collection(self, collection_id: str, workflow_id: str):
        """Add a workflow to a collection by its ID"""
        try:
            collection = self.collections_api.collections_get_collection(collection_id)
            if not collection:
                return "Error: Collection not found"
            workflow = self.workflows_api.workflows_get_workflow(workflow_id)
            if not workflow:
                return "Error: Workflow not found"
            contract = server_client.AddWorkflowContract(workflow_id=workflow_id)
            api_response = self.collections_api.collections_add_workflow_to_collection(collection_id, contract)
            return pprint.pformat(api_response)
        except ApiException as e:
            return f"Error: {e}"

    def remove_workflow_from_collection(self, collection_id: str, workflow_id: str):
        """Remove a workflow from a collection by its ID"""
        try:
            collection = self.collections_api.collections_get_collection(collection_id)
            if not collection:
                return "Error: Collection not found"
            workflow = self.workflows_api.workflows_get_workflow(workflow_id)
            if not workflow:
                return "Error: Workflow not found"
            api_response = self.collections_api.collections_remove_workflow_from_collection(collection_id, workflow_id)
            return pprint.pformat(api_response)
        except ApiException as e:
            return f"Error: {e}"

    def add_schedule_to_collection(self, collection_id: str, schedule_id: str):
        """Add a schedule to a collection by its ID"""
        try:
            collection = self.collections_api.collections_get_collection(collection_id)
            if not collection:
                return "Error: Collection not found"
            schedule = self.schedules_api.schedules_get_schedule(schedule_id)
            if not schedule:
                return "Error: Schedule not found"
            contract = server_client.AddScheduleContract(schedule_id=schedule_id)
            api_response = self.collections_api.collections_add_schedule_to_collection(collection_id, contract)
            return pprint.pformat(api_response)
        except ApiException as e:
            return f"Error: {e}"

    def remove_schedule_from_collection(self, collection_id: str, schedule_id: str):
        """Remove a schedule from a collection by its ID"""
        try:
            collection = self.collections_api.collections_get_collection(collection_id)
            if not collection:
                return "Error: Collection not found"
            schedule = self.schedules_api.schedules_get_schedule(schedule_id)
            if not schedule:
                return "Error: Schedule not found"
            api_response = self.collections_api.collections_remove_schedule_from_collection(collection_id, schedule_id)
            return pprint.pformat(api_response)
        except ApiException as e:
            return f"Error: {e}"

    # Workflows functions
    def get_all_workflows(self):
        """Get the list of all workflows of the Alteryx server"""
        try:
            api_response = self.workflows_api.workflows_get_workflows()
            return pprint.pformat(api_response)
        except ApiException as e:
            return f"Error: {e}"

    def get_workflow_by_id(self, workflow_id: str):
        """Get a workflow by its ID"""
        try:
            api_response = self.workflows_api.workflows_get_workflow(workflow_id)
            return pprint.pformat(api_response)
        except ApiException as e:
            return f"Error: {e}"

    def update_workflow_name_or_comment(self, workflow_id: str, name: str, comment: str):
        """Update a workflow name or comment by its ID"""
        try:
            workflow = self.workflows_api.workflows_get_workflow(workflow_id)
            if not workflow:
                return "Error: Workflow not found"
            workflow_details = server_client.WorkflowView(**workflow)
            latest_version_id = server_client.WorkflowVersionView(
                **workflow_details.versions[len(workflow_details.versions) - 1]
            ).version_id
            contract = server_client.UpdateWorkflowContract(
                name=name if name else workflow_details.name,
                version_id=latest_version_id,
                make_published=workflow_details.is_public,
                owner_id=workflow_details.owner_id,
                worker_tag=workflow_details.worker_tag,
                district_tags=workflow_details.district_tags,
                comment=comment if comment else workflow_details.comments,
                is_public=workflow_details.is_public,
                is_ready_for_migration=workflow_details.is_ready_for_migration,
                others_may_download=workflow_details.others_may_download,
                others_can_execute=workflow_details.others_can_execute,
                execution_mode=workflow_details.execution_mode,
                has_private_data_exemption=workflow_details.has_private_data_exemption,
            )
            api_response = self.workflows_api.workflows_update_workflow(workflow_id, contract)
            return pprint.pformat(api_response)
        except ApiException as e:
            return f"Error: {e}"

    def transfer_workflow(self, workflow_id: str, new_owner_id: str):
        """Transfer a workflow to a new owner by its ID"""
        try:
            workflow = self.workflows_api.workflows_get_workflow(workflow_id)
            if not workflow:
                return "Error: Workflow not found"
            new_owner = self.users_api.users_get_user(new_owner_id)
            if not new_owner:
                return "Error: New owner not found"
            contract = server_client.TransferWorkflowContract(owner_id=new_owner_id)
            api_response = self.workflows_api.workflows_transfer_workflow(workflow_id, contract)
            return pprint.pformat(api_response)
        except ApiException as e:
            return f"Error: {e}"

    def get_workflow_jobs(self, workflow_id: str):
        """Get the list of jobs for an existing workflow"""
        try:
            workflow = self.workflows_api.workflows_get_workflow(workflow_id)
            if not workflow:
                return "Error: Workflow not found"
            api_response = self.workflows_api.workflows_get_jobs_for_workflow(workflow_id)
            return pprint.pformat(api_response)
        except ApiException as e:
            return f"Error: {e}"

    def execute_workflow(self, workflow_id: str, input_data: list[InputData] = None):
        """Execute a workflow its ID. This will create a new job and add it to the execution queue.
        This call will return a job ID that can be used to get the job details.
        The input data is a list of name-value pairs, each containing a name and value."""
        try:
            workflow = self.workflows_api.workflows_get_workflow(workflow_id)
            if not workflow:
                return "Error: Workflow not found"
            questions = self.workflows_api.workflows_get_workflow_questions(workflow_id)
            if (not questions or len(questions) == 0) and (input_data):
                return "Error: Workflow has no questions, input data not allowed"
            if questions and len(questions) > 0:
                for question in questions:
                    if question.name not in [item.name for item in input_data]:
                        return f"Error: Input data must contain the question '{question.name}'"
            workflow = server_client.WorkflowView(**workflow)
            contract = server_client.EnqueueJobContract(worker_tag=workflow.worker_tag, questions=input_data)
            api_response = self.workflows_api.workflows_enqueue(workflow_id, contract)
            return pprint.pformat(api_response)
        except ApiException as e:
            return f"Error: {e}"

    # Users functions
    def get_all_users(self):
        """Get the list of all users of the Alteryx server"""
        try:
            api_response = self.users_api.users_get_users()
            return pprint.pformat(api_response)
        except ApiException as e:
            return f"Error: {e}"

    def get_user_by_id(self, user_id: str):
        """Get a user by their ID"""
        try:
            api_response = self.users_api.users_get_user(user_id)
            return pprint.pformat(api_response)
        except ApiException as e:
            return f"Error: {e}"

    def get_user_by_email(self, email: str):
        """Get a user by their email"""
        try:
            api_response = self.users_api.users_get_users(email=email)
            return pprint.pformat(api_response)
        except ApiException as e:
            return f"Error: {e}"

    def get_user_by_name(self, name: str):
        """Get a user by their last name"""
        try:
            api_response = self.users_api.users_get_users(last_name=name)
            return pprint.pformat(api_response)
        except ApiException as e:
            return f"Error: {e}"

    def get_user_by_first_name(self, first_name: str):
        """Get a user by their first name"""
        try:
            api_response = self.users_api.users_get_users(first_name=first_name)
            return pprint.pformat(api_response)
        except ApiException as e:
            return f"Error: {e}"

    def get_all_user_assets(self, user_id: str):
        """Get all the assets for a user"""
        try:
            api_response = self.users_api.users_get_users_assets(user_id)
            return pprint.pformat(api_response)
        except ApiException as e:
            return f"Error: {e}"

    def get_user_assets_by_type(self, user_id: str, asset_type: str):
        """Get all the assets for a user by type. The asset type can be 'Workflow', 'Collection',
        'Connection', 'Credential' or 'All'."""
        try:
            api_response = self.users_api.users_get_users_assets(user_id, asset_type)
            return pprint.pformat(api_response)
        except ApiException as e:
            return f"Error: {e}"

    def update_user_details(self, user_id: str, first_name: str, last_name: str, email: str):
        """Update details of an existing user by their ID. Can be used to update any of the user's details."""
        try:
            user_details = self.users_api.users_get_user(user_id)
            user_details = server_client.UserView(**user_details)
            if not user_details:
                return "Error: User not found"
            contract = server_client.UpdateUserContract(
                id=user_details.id,
                first_name=first_name if first_name else user_details.first_name,
                last_name=last_name if last_name else user_details.last_name,
                email=email if email else user_details.email,
                role=user_details.role,
                default_worker_tag=user_details.default_worker_tag,
                can_schedule_jobs=user_details.can_schedule_jobs,
                can_prioritize_jobs=user_details.can_prioritize_jobs,
                can_assign_jobs=user_details.can_assign_jobs,
                can_create_collections=user_details.can_create_collections,
                is_api_enabled=user_details.is_api_enabled,
                default_credential_id=user_details.default_credential_id,
                is_account_locked=user_details.is_account_locked,
                is_active=user_details.is_active,
                is_validated=user_details.is_validated,
                time_zone=user_details.time_zone,
                language=user_details.language,
                can_create_and_update_dcm=user_details.can_create_and_update_dcm,
                can_share_for_execution_dcm=user_details.can_share_for_execution_dcm,
                can_share_for_collaboration_dcm=user_details.can_share_for_collaboration_dcm,
                can_manage_generic_vaults_dcm=user_details.can_manage_generic_vaults_dcm,
            )
            api_response = self.users_api.users_update_user(user_id, contract)
            return pprint.pformat(api_response)
        except ApiException as e:
            return f"Error: {e}"

    def transfer_all_assets(
        self,
        user_id: str,
        new_owner_id: str,
        transfer_workflows: bool,
        transfer_schedules: bool,
        transfer_collections: bool,
    ):
        """Transfer all assets (workflows, schedules, collections) owned by one user to another."""
        try:
            user = self.users_api.users_get_user(user_id)
            if not user:
                return "Error: User not found"
            new_owner = self.users_api.users_get_user(new_owner_id)
            if not new_owner:
                return "Error: New owner not found"
            contract = server_client.TransferUserAssetsContract(
                owner_id=new_owner_id,
                transfer_workflows=transfer_workflows,
                transfer_schedules=transfer_schedules,
                transfer_collections=transfer_collections,
            )
            api_response = self.users_api.users_transfer_assets(user_id, contract)
            return pprint.pformat(api_response)
        except ApiException as e:
            return f"Error: {e}"

    def deactivate_user(self, user_id: str):
        """Deactivate a user by their ID"""
        try:
            user = self.users_api.users_get_user(user_id)
            if not user:
                return "Error: User not found"
            api_response = self.users_api.users_deactivate_user(user_id)
            return pprint.pformat(api_response)
        except ApiException as e:
            return f"Error: {e}"

    def reset_user_password(self, user_id: str):
        """Reset a user's password by their ID"""
        try:
            user = self.users_api.users_get_user(user_id)
            if not user:
                return "Error: User not found"
            api_response = self.users_api.users_reset_user_password(user_id)
            return pprint.pformat(api_response)
        except ApiException as e:
            return f"Error: {e}"

    # Jobs functions
    def get_all_job_messages(self, job_id: str):
        """Get all the messages for a job"""
        try:
            api_response = self.jobs_api.jobs_get_job_v3(job_id, include_messages=True)
            return pprint.pformat(api_response)
        except ApiException as e:
            return f"Error: {e}"

    def get_job_by_id(self, job_id: str):
        """Retrieve details about an existing job and its current state. Only app workflows can be used."""
        try:
            api_response = self.jobs_api.jobs_get_job_v3(job_id)
            return pprint.pformat(api_response)
        except ApiException as e:
            return f"Error: {e}"

    # Schedules functions
    def get_all_schedules(self):
        """Get the list of all schedules of the Alteryx server"""
        try:
            api_response = self.schedules_api.schedules_get_schedules()
            return pprint.pformat(api_response)
        except ApiException as e:
            return f"Error: {e}"

    def get_schedule_by_id(self, schedule_id: str):
        """Get a schedule by its ID"""
        try:
            api_response = self.schedules_api.schedules_get_schedule(schedule_id)
            return pprint.pformat(api_response)
        except ApiException as e:
            return f"Error: {e}"

    def deactivate_schedule(self, schedule_id: str):
        """Deactivate a schedule by its ID"""
        try:
            schedule = self.schedules_api.schedules_get_schedule(schedule_id)
            if not schedule:
                return "Error: Schedule not found"
            schedule = server_client.ScheduleView(**schedule)
            contract = server_client.UpdateScheduleContract(
                workflow_id=schedule.workflow_id,
                owner_id=schedule.owner_id,
                iteration=schedule.iteration,
                name=schedule.name,
                comment=schedule.comment,
                priority=schedule.priority,
                worker_tag=schedule.worker_tag,
                enabled=False,
                credential_id=schedule.credential_id,
                time_zone=schedule.time_zone,
                questions=schedule.questions,
            )
            api_response = self.schedules_api.schedules_update_schedule(schedule_id, contract)
            return pprint.pformat(api_response)
        except ApiException as e:
            return f"Error: {e}"

    def activate_schedule(self, schedule_id: str):
        """Activate a schedule by its ID"""
        try:
            schedule = self.schedules_api.schedules_get_schedule(schedule_id)
            if not schedule:
                return "Error: Schedule not found"
            schedule = server_client.ScheduleView(**schedule)
            contract = server_client.UpdateScheduleContract(
                workflow_id=schedule.workflow_id,
                owner_id=schedule.owner_id,
                iteration=schedule.iteration,
                name=schedule.name,
                comment=schedule.comment,
                priority=schedule.priority,
                worker_tag=schedule.worker_tag,
                enabled=True,
                credential_id=schedule.credential_id,
                time_zone=schedule.time_zone,
                questions=schedule.questions,
            )
            api_response = self.schedules_api.schedules_update_schedule(schedule_id, contract)
            return pprint.pformat(api_response)
        except ApiException as e:
            return f"Error: {e}"

    def update_schedule_name_or_comment(self, schedule_id: str, name: str, comment: str):
        """Update the name or comment of a schedule by its ID"""
        try:
            schedule = self.schedules_api.schedules_get_schedule(schedule_id)
            if not schedule:
                return "Error: Schedule not found"
            schedule = server_client.ScheduleView(**schedule)
            contract = server_client.UpdateScheduleContract(
                workflow_id=schedule.workflow_id,
                owner_id=schedule.owner_id,
                iteration=schedule.iteration,
                name=name if name else schedule.name,
                comment=comment if comment else schedule.comment,
                priority=schedule.priority,
                worker_tag=schedule.worker_tag,
                enabled=schedule.enabled,
                credential_id=schedule.credential_id,
                time_zone=schedule.time_zone,
                questions=schedule.questions,
            )
            api_response = self.schedules_api.schedules_update_schedule(schedule_id, contract)
            return pprint.pformat(api_response)
        except ApiException as e:
            return f"Error: {e}"

    def change_schedule_owner(self, schedule_id: str, new_owner_id: str):
        """Change the owner of a schedule by its ID"""
        try:
            schedule = self.schedules_api.schedules_get_schedule(schedule_id)
            if not schedule:
                return "Error: Schedule not found"
            schedule = server_client.ScheduleView(**schedule)
            contract = server_client.UpdateScheduleContract(
                workflow_id=schedule.workflow_id,
                owner_id=new_owner_id if new_owner_id else schedule.owner_id,
                iteration=schedule.iteration,
                name=schedule.name,
                comment=schedule.comment,
                priority=schedule.priority,
                worker_tag=schedule.worker_tag,
                enabled=schedule.enabled,
                credential_id=schedule.credential_id,
                time_zone=schedule.time_zone,
                questions=schedule.questions,
            )
            api_response = self.schedules_api.schedules_update_schedule(schedule_id, contract)
            return pprint.pformat(api_response)
        except ApiException as e:
            return f"Error: {e}"

    # Credentials functions
    def get_all_credentials(self):
        """Get the list of all accessible credentials of the Alteryx server"""
        try:
            api_response = self.credentials_api.credentials_get_credentials()
            return pprint.pformat(api_response)
        except ApiException as e:
            return f"Error: {e}"

    def get_credential_by_id(self, credential_id: str):
        """Get the details of an existing credential."""
        try:
            api_response = self.credentials_api.credentials_get_credential(credential_id)
            return pprint.pformat(api_response)
        except ApiException as e:
            return f"Error: {e}"

    # Connections functions
    def lookup_connection(self, connection_id: str):
        """Lookup a DCM Connection as referenced in workflows"""
        try:
            api_response = self.dcm_api.d_cme_lookup_dcm_connection(connection_id)
            return pprint.pformat(api_response)
        except ApiException as e:
            return f"Error: {e}"

    def get_connection_by_id(self, connection_id: str):
        """Get a connection by its ID"""
        try:
            api_response = self.dcm_api.d_cme_get_dcm_connection(connection_id)
            return pprint.pformat(api_response)
        except ApiException as e:
            return f"Error: {e}"

    # Workflow file functions
    def download_workflow_package_file(self, workflow_id: str, output_directory: str):
        """Download a workflow package file by its ID and save it to the local directory"""
        try:
            api_response = self.workflows_api.workflows_get_workflow(workflow_id)
            if api_response is None:
                return "Error: Workflow not found"
            
            # Download the workflow file
            api_response = self.workflows_api.workflows_download_workflow(workflow_id)
            if api_response is None:
                return "Error: Failed to download workflow"
            
            # Create the output directory if it doesn't exist
            if not os.path.exists(output_directory):
                os.makedirs(output_directory)
            
            # Save the workflow file to the output directory
            with open(
                f"{output_directory}/{workflow_id}.yxzp",
                "wb" if not os.path.exists(f"{output_directory}/{workflow_id}.yxzp") else "wb+",
            ) as f:
                f.write(api_response)

            return (
                f"Workflow {workflow_id} downloaded successfully. File saved to '{output_directory}/{workflow_id}.yxzp'"
            )
        except ApiException as e:
            return f"Error: {e.body}"

    def get_workflow_xml(self, workflow_id: str):
        """Get the XML representation of a workflow file by its ID"""
        try:
            api_response = self.workflows_api.workflows_get_workflow(workflow_id)
            if api_response is None:
                return "Error: Workflow not found"
            
             # Download the workflow file
            api_response = self.workflows_api.workflows_download_workflow(workflow_id)
            if api_response is None:
                return "Error: Failed to download workflow"
                
            temp_directory = tempfile.gettempdir()
            
            with open(
                f"{temp_directory}/{workflow_id}.yxzp",
                "wb" if not os.path.exists(f"{temp_directory}/{workflow_id}.yxz") else "wb+",
            ) as f:
                f.write(api_response)

            new_directory = f"{temp_directory}/{workflow_id}"
            if os.path.exists(new_directory):
                shutil.rmtree(new_directory)
            os.makedirs(new_directory)
            
            with zipfile.ZipFile(f"{temp_directory}/{workflow_id}.yxzp", "r") as zip_ref:
                zip_ref.extractall(new_directory)
            
            yxmd_files = [file for file in os.listdir(new_directory) if file.endswith(".yxmd")]
            if len(yxmd_files) == 0:
                return "Error: Workflow XML file not found after unzipping"
            
            yxmd_file = yxmd_files[0]
            
            # Read as binary first, then decode as UTF-8
            with open(f"{new_directory}/{yxmd_file}", "rb") as f:
                binary_content = f.read()
                try:
                    # Try to decode as UTF-8
                    return binary_content.decode('utf-8')
                except UnicodeDecodeError:
                    # If UTF-8 fails, return the binary content as a string representation
                    return binary_content
            
        except ApiException as e:
            return f"Error: {e}"
