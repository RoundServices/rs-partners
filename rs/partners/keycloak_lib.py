# rs-partners is available under the MIT License. https://gitlab.com/roundservices/gluu-commons/
# Copyright (c) 2020, Round Services LLC - https://roundservices.biz/
#
# Author: Gustavo J Gallardo - ggallard@roundservices.biz
#

import json
import os
import shutil
from keycloak import KeycloakAdmin
# needed for override methods
from keycloak.exceptions import raise_error_from_response, KeycloakGetError
from keycloak.urls_patterns import URL_ADMIN_CLIENT_SCOPES, URL_ADMIN_CLIENT, URL_ADMIN_FLOWS, URL_ADMIN_FLOWS_EXECUTIONS

URL_ADMIN_CLIENT_SERVICE_ACCOUNT_USER = URL_ADMIN_CLIENT + "/service-account-user"
URL_ADMIN_FLOW = URL_ADMIN_FLOWS + "{id}"
URL_ADMIN_FLOWS_EXECUTION = URL_ADMIN_FLOWS_EXECUTIONS + "/execution"
URL_ADMIN_EXECUTION = "admin/realms/{realm-name}/authentication/executions/{id}"
URL_ADMIN_FLOWS_EXECUTIONS_FLOW = URL_ADMIN_FLOWS_EXECUTIONS + "/flow"


class RSKeycloakAdmin(KeycloakAdmin):
	def __init__(self, logger, local_properties, server_url, username=None, password=None, realm_name='master', client_id='admin-cli', verify=True, client_secret_key=None, custom_headers=None, user_realm_name=None, auto_refresh_token=None):
		KeycloakAdmin.__init__(self, server_url, username, password, realm_name, client_id, verify, client_secret_key, custom_headers, user_realm_name, auto_refresh_token)
		self.logger = logger
		self.local_properties = local_properties

# ###########################
# Override methods
	def create_client_scope(self, payload, skip_exists=False):
		"""
		Create a client scope

		ClientScopeRepresentation: https://www.keycloak.org/docs-api/8.0/rest-api/index.html#_getclientscopes

		:param payload: ClientScopeRepresentation
		:param skip_exists: If true then do not raise an error if client scope already exists
		:return:  Keycloak server response (ClientScopeRepresentation)
		"""
		params_path = {"realm-name": self.realm_name}
		data_raw = self.raw_post(URL_ADMIN_CLIENT_SCOPES.format(**params_path), data=json.dumps(payload))
		return raise_error_from_response(data_raw, KeycloakGetError, expected_codes=[201], skip_exists=skip_exists)


	def get_client_service_account_user(self, client_id):
		"""
		Get service account user from client.

		:param client_id: id in ClientRepresentation
		https://www.keycloak.org/docs-api/8.0/rest-api/index.html#_clientrepresentation
		:return: UserRepresentation
		"""
		params_path = {"realm-name": self.realm_name, "id": client_id}
		data_raw = self.raw_get(URL_ADMIN_CLIENT_SERVICE_ACCOUNT_USER.format(**params_path))
		return raise_error_from_response(data_raw, KeycloakGetError)


	def delete_authentication_flow(self, flow_id):
		"""
		Delete authentication flow execution

		AuthenticationExecutionInfoRepresentation
		https://www.keycloak.org/docs-api/8.0/rest-api/index.html#_authenticationexecutioninforepresentation

		:param flow_id: authentication flow id
		:return: Keycloak server response
		"""
		params_path = {"realm-name": self.realm_name, "id": flow_id}
		data_raw = self.raw_delete(URL_ADMIN_FLOW.format(**params_path))
		return raise_error_from_response(data_raw, KeycloakGetError, expected_codes=[204])


	def create_authentication_flow_execution(self, payload, flow_alias):
		"""
		Create a new authentication flow execution

		AuthenticationExecutionInfoRepresentation
		https://www.keycloak.org/docs-api/8.0/rest-api/index.html#_authenticationexecutioninforepresentation

		:param payload: AuthenticationExecutionInfoRepresentation
		:param skip_exists: If true then do not raise an error if authentication execution flow already exists
		:return: Keycloak server response (AuthenticationExecutionInfoRepresentation)
		"""
		params_path = {"realm-name": self.realm_name, "flow-alias": flow_alias}
		data_raw = self.raw_post(URL_ADMIN_FLOWS_EXECUTION.format(**params_path), data=json.dumps(payload))
		raise_error_from_response(data_raw, KeycloakGetError, expected_codes=[201])
		return data_raw.headers['Location'].split('/')[-1]


	def delete_authentication_flow_execution(self, execution_id):
		"""
		Delete authentication flow execution

		AuthenticationExecutionInfoRepresentation
		https://www.keycloak.org/docs-api/8.0/rest-api/index.html#_authenticationexecutioninforepresentation

		:param execution_id: keycloak client id (not oauth client-id)
		:return: Keycloak server response (ClientRepresentation)
		"""
		params_path = {"realm-name": self.realm_name, "id": execution_id}
		data_raw = self.raw_delete(URL_ADMIN_EXECUTION.format(**params_path))
		return raise_error_from_response(data_raw, KeycloakGetError, expected_codes=[204])


	def update_authentication_flow_executions(self, payload, flow_alias):
		"""
		Update an authentication flow execution
		AuthenticationExecutionInfoRepresentation
		https://www.keycloak.org/docs-api/8.0/rest-api/index.html#_authenticationexecutioninforepresentation
		:param payload: AuthenticationExecutionInfoRepresentation
		:param flow_alias: The flow alias
		:return: Keycloak server response
		"""
		params_path = {"realm-name": self.realm_name, "flow-alias": flow_alias}
		data_raw = self.raw_put(URL_ADMIN_FLOWS_EXECUTIONS.format(**params_path), data=json.dumps(payload))
		return raise_error_from_response(data_raw, KeycloakGetError, expected_codes=[202, 204])


	def add_authentication_flow_executions_flow(self, payload, flow_alias, skip_exists=False):
		"""
		Add new flow with new execution to existing flow

		:param payload: New authentication flow / execution JSON data containing 'alias', 'type', 'provider', and 'description' attributes
		:param flow_alias: The flow alias
		:return: Keycloak server response
		"""
		params_path = {"realm-name": self.realm_name, "flow-alias": flow_alias}
		data_raw = self.raw_post(URL_ADMIN_FLOWS_EXECUTIONS_FLOW.format(**params_path), data=json.dumps(payload))
		raise_error_from_response(data_raw, KeycloakGetError, expected_codes=[201], skip_exists=skip_exists)
		return data_raw.headers['Location'].split('/')[-1]

# ###########################
# Added methods
	def rs_client_exists(self, client_id):
		clients = self.get_clients()
		for client in clients:
			self.logger.trace("client: {}", client)
			self.logger.trace("client_id: {}", client["clientId"])
			if client["clientId"] == client_id:
				return True
		return False


	def rs_delete_client(self, client_id):
		clients = self.get_clients()
		for client in clients:
			self.logger.trace("client: {}", client)
			self.logger.trace("client_id: {}", client["clientId"])
			if client["clientId"] == client_id:
				self.delete_client(client["id"])
		return False


	def rs_component_exists(self, component_id, parent, provider_type):
		query = {"parent":parent, "type":provider_type}
		self.logger.trace("query: {}", query)
		components = self.get_components(query=query)
		for component in components:
			self.logger.trace("component: {}", component)
			self.logger.trace("component_id: {}", component["id"])
			if component["id"] == component_id:
				return True
		return False


	def rs_delete_component_childs(self, component_id):
		query = {"parent": component_id}
		self.logger.trace("query: {}", query)
		components = self.get_components(query=query)
		for component in components:
			self.logger.debug("Deleting component_id: {}", component["id"])
			self.delete_component(component["id"])


	def rs_get_authentication_flow(self, flow_alias):
		authentication_flows = self.get_authentication_flows()
		for authentication_flow in authentication_flows:
			self.logger.trace("authentication_flow: {}", authentication_flow)
			self.logger.trace("authentication_flow_id: {}", authentication_flow["id"])
			self.logger.debug("authentication_flow_alias: {}", authentication_flow["alias"])
			if authentication_flow["alias"] == flow_alias:
				return authentication_flow
		return None


	def rs_get_execution_flow(self, flow_alias, execution_flow_id):
		executions = self.get_authentication_flow_executions(flow_alias)
		self.logger.debug("Getting execution flow with id: {} from authentication flow: {}. Executions: {}", execution_flow_id, flow_alias, executions)
		for execution in executions:
			self.logger.trace("_rs_get_execution_flow() execution_flow: {}", execution)
			self.logger.trace("_rs_get_execution_flow() execution_flow_id: {}", execution["id"])
			if "flowId" in execution:
				if execution["flowId"] == execution_flow_id:
					return execution
		return None


	def rs_create_realm(self, realm_json_file, temp_file):
		shutil.copyfile(realm_json_file, temp_file)
		self.local_properties.replace(temp_file)
		with open(temp_file) as json_file:
			json_data = json.load(json_file)
			self.logger.trace("json_data: {}", json_data)
			self.create_realm(json_data, skip_exists=True)


	def rs_update_realm_attributes(self, objects_folder, realm_name, temp_file):
		self.logger.debug("Importing realm attributes")
		for directory_entry in sorted(os.scandir(objects_folder), key=lambda path: path.name):
			if directory_entry.is_file() and directory_entry.path.endswith(".json"):
				self.logger.debug("Processing file: {}", directory_entry.path)
				shutil.copyfile(directory_entry.path, temp_file)
				self.local_properties.replace(temp_file)
				with open(temp_file) as json_file:
					json_data = json.load(json_file)
					self.logger.trace("json_data: {}", json_data)
					self.update_realm(realm_name, json_data)


	def rs_import_components(self, objects_folder, realm_id, temp_file):
		self.logger.debug("Importing components from: {}", objects_folder)
		for directory_entry in sorted(os.scandir(objects_folder), key=lambda path: path.name):
			if directory_entry.is_file() and directory_entry.path.endswith(".json"):
				self.logger.debug("Processing file: {}", directory_entry.path)
				shutil.copyfile(directory_entry.path, temp_file)
				self.local_properties.replace(temp_file)
				with open(temp_file) as json_file:
					json_data = json.load(json_file)
					self.logger.trace("Component definition: {}", json_data)
					component_id = json_data["id"]
					provider_type = json_data["providerType"]
					if "parentId" in json_data:
						parent = json_data["parentId"]
					else:
						parent = realm_id
					if self.rs_component_exists(component_id, parent, provider_type):
						self.logger.debug("Component '{}' already exists. Updating...", component_id)
						self.update_component(component_id, json_data)
					else:
						self.logger.debug("Component '{}' does not exist. Creating...", component_id)
						self.create_component(json_data)
						self.logger.debug("Deleting default childs for component_id:  ", component_id)
						self.rs_delete_component_childs(component_id)


	def rs_import_authentication_flows(self, objects_folder, temp_file):
		self.logger.debug("Importing authentication flows")
		for directory_entry in sorted(os.scandir(objects_folder), key=lambda path: path.name):
			if directory_entry.is_file() and directory_entry.path.endswith(".json"):
				self.logger.debug("Processing file: {}", directory_entry.path)
				shutil.copyfile(directory_entry.path, temp_file)
				self.local_properties.replace(temp_file)
				with open(temp_file) as json_file:
					authentication_flow = json.load(json_file)
					authentication_executions = authentication_flow["authenticationExecutions"]
					self.logger.trace("json_data: {}", authentication_flow)
					# Create flow without executions (if flow does not exist)
					authentication_flow.pop("authenticationExecutions", None)
					self.logger.debug("Creating Authentication Flow using: {}", authentication_flow)
					flow_alias = authentication_flow["alias"]
					self.logger.trace("Flow alias: {}", flow_alias)
					self.create_authentication_flow(json.dumps(authentication_flow), skip_exists=True)
					# Delete any current (level=0) executions from flow
					current_executions = self.get_authentication_flow_executions(flow_alias)
					self.logger.trace("Current executions for flow alias '{}': {}", flow_alias, current_executions)
					for current_execution in current_executions:
						if current_execution["level"] == 0:
							self.logger.debug("Deleting authentication execution: {}", current_execution)
							self.delete_authentication_flow_execution(current_execution["id"])
					# Add new executions
					for authentication_execution in authentication_executions:
						self.logger.debug("Processing authentication execution: {}", authentication_execution)
						if "alias" in authentication_execution:
							# if execution flow, delete and re-create
							execution_alias = authentication_execution["alias"]
							execution_flow = self.rs_get_authentication_flow(execution_alias)
							if execution_flow is not None:
								self.delete_authentication_flow(execution_flow["id"])
							# add new execution flow
							add_payload = {}
							add_payload["alias"] = execution_alias
							add_payload["type"] = "basic-flow"
							add_payload["provider"] = "registration-page-form"
							add_payload["description"] = ""
							self.logger.debug("Adding execution flow: {}", add_payload)
							execution_flow_id = self.add_authentication_flow_executions_flow(add_payload, flow_alias, skip_exists=False)
							self.logger.trace("Execution flow creation returned id: {}", execution_flow_id)
							execution_flow = self.rs_get_execution_flow(flow_alias, execution_flow_id)
							self.logger.trace("Current Execution Flow: {}", execution_flow)
							execution_id = execution_flow["id"]
							update_payload = {}
							update_payload["id"] = execution_id
							for attr, value in authentication_execution.items():
								if attr != "alias":
									self.logger.debug("Set attr: {} with value: {} in the execution_flow", attr, value)
									update_payload[attr] = value
							self.logger.debug("Update execution in {} with: {}", flow_alias, update_payload)
							self.update_authentication_flow_executions(update_payload, flow_alias)
						else:
							create_payload = {}
							create_payload["provider"] = authentication_execution["providerId"]
							self.logger.debug("Creating Authentication Flow Execution using: {}", create_payload)
							created_flow_execution = self.create_authentication_flow_execution(create_payload, flow_alias)
							self.logger.trace("Created Authentication Flow Execution: {}", created_flow_execution)
							authentication_execution["id"] = created_flow_execution
							self.logger.debug("Updating Authentication Flow Execution using: {}", authentication_execution)
							self.update_authentication_flow_executions(authentication_execution, flow_alias)


	def rs_get_execution_by_provider(self, flow_alias, execution_provider_id):
		executions = self.get_authentication_flow_executions(flow_alias)
		for execution in executions:
			self.logger.trace("execution: {}", execution)
			if execution["providerId"] == execution_provider_id:
				return execution
		return None


	def rs_set_execution_attribute(self, flow_alias, execution_provider_id, attr_name, attr_value):
		execution = self.rs_get_execution_by_provider(flow_alias, execution_provider_id)
		self.logger.debug("Current execution: {}", execution)
		execution[attr_name] = attr_value
		self.logger.debug("Updating execution to: {}", execution)
		self.update_authentication_flow_executions(execution, flow_alias)


	def rs_create_client_scopes(self, objects_folder, temp_file):
		self.logger.debug("Importing client scopes")
		for directory_entry in sorted(os.scandir(objects_folder), key=lambda path: path.name):
			if directory_entry.is_file() and directory_entry.path.endswith(".json"):
				self.logger.debug("Processing file: {}", directory_entry.path)
				shutil.copyfile(directory_entry.path, temp_file)
				self.local_properties.replace(temp_file)
				with open(temp_file) as json_file:
					json_data = json.load(json_file)
					self.logger.trace("json_data: {}", json_data)
					self.create_client_scope(json_data, skip_exists=True)


	def rs_import_clients(self, objects_folder, temp_file):
		self.logger.debug("Importing clients from: {}", objects_folder)
		for directory_entry in sorted(os.scandir(objects_folder), key=lambda path: path.name):
			if directory_entry.is_file() and directory_entry.path.endswith(".json"):
				self.logger.debug("Processing file: {}", directory_entry.path)
				shutil.copyfile(directory_entry.path, temp_file)
				self.local_properties.replace(temp_file)
				with open(temp_file) as json_file:
					json_data = json.load(json_file)
					self.logger.trace("Client definition: {}", json_data)
					client_id = json_data["clientId"]
					if self.rs_client_exists(client_id):
						client_keycloak_id = self.get_client_id(client_id)
						self.logger.debug("Client '{}' already exists with internal id: {}. Updating...", client_id, client_keycloak_id)
						self.update_client(client_keycloak_id, json_data)
					else:
						self.logger.debug("Client '{}' does not exist. Creating...", client_id)
						self.create_client(json_data, skip_exists=True)


	def rs_assign_roles_to_client(self, client, role_names):
		client_id = self.get_client_id(client)
		self.logger.debug("client_id: {}", client_id)
		user_id = self.get_client_service_account_user(client_id)["id"]
		self.logger.debug("user_id: {}", user_id)
		realm_management_client_id = self.get_client_id("realm-management")
		for role_name in role_names:
			role = self.get_client_role(realm_management_client_id, role_name)
			self.logger.debug("role: {}", role)
			self.assign_client_role(client_id=realm_management_client_id, user_id=user_id, roles=role)

