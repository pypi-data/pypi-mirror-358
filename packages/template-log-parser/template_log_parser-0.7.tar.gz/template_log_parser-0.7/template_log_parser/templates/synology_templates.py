from template_log_parser.column_functions import (
    calc_data_usage,
    isolate_ip_from_parentheses,
)

# Tasks
backup_task = "{time} {server_name} {package_name} {system_user}:#011[{type}][{task_name}] {message}"
backup_version_rotation = "{time} {server_name} {package_name} {system_user}:#011[{task_name}] Trigger version rotation."
backup_version_rotation_status = "{time} {server_name} {package_name}: {system_user}:#011[{task_name}] Version rotation {status} from ID [{id}]."
backup_rotate_version = "{time} {server_name} {package_name}: {system_user}:#011[{task_name}] Rotate version [{version}] from ID [{id}]."
scheduled_task_message = "{time} {server_name} System {system_user}:#011Scheduled Task [{task_name}] {message}"
hyper_backup_task_message = "{time} {server_name} Hyper_Backup: {system_user}:#011Backup task [{task_name}] {message}"
task_setting = "{time} {server_name} {package_name}: {system_user}:#011Setting of {message}"
credentials_changed = "{time} {server_name} {package_name} {system_user}:#011[{type}] Credentials changed on the destination."

# General System
auto_install = "{time} {server_name} System {system_user}:#011Start install [{package}] automatically."
back_online = "{time} {server_name} System {system_user}:#011Server back online."
countdown = "{time} {server_name} System {system_user}:#011System started counting down to {state}."
dns_setting_changed = "{time} {server_name} System {system_user}:#011DNS server setting was changed."
download_task = "{time} {server_name} System {system_user}:#011Download task for [{task}] {result}."
failed_video_conversion = "{time} {server_name} System {system_user}:#011System failed to convert video [{video}] to {format}."
interface_set = "{time} {server_name} System {system_user}:#011[{interface}] was set to [{set_to}]."
interface_changed = "{time} {server_name} System {system_user}:#011{attribute} of [{interface}] was changed from [{from}] to [{to}]."
link_state = "{time} {server_name} System {system_user}:#011[{interface}] link {state}."
on_battery = "{time} {server_name} System {system_user}:#011Server is on battery."
package_change = "{time} {server_name} System {system_user}:#011Package [{package}] has been successfully {state}."
process_start_or_stop = "{time} {server_name} System: System successfully {result} [{process}]."
scrubbing = "{time} {server_name} System {system_user}:#011System {state} {type} scrubbing on [{location}]."
service_started_or_stopped = "{time} {server_name} System {system_user}:#011[{service}] service was {state}."
restarted_service = "{time} {server_name} System {system_user}:#011System successfully restarted {service} service."
shared_folder = "{time} {server_name} System {system_user}:#011{kind} shared folder [{shared_folder}] {message}"
shared_folder_application = "{time} {server_name} System {system_user}:#011Shared folder [{shared_folder}] {message} [{application}]."
setting_enabled = "{time} {server_name} System {system_user}:#011[{setting}] was enabled."
update = "{time} {server_name} System {system_user}:#011Update was {result}."
unknown_error = "{time} {server_name} System {system_user}:#011An unknown error occurred, {message}"

# User Activity
blocked = "{time} {server_name} System {user}:#011Host [{client_ip}] was blocked via [{service}]."
unblock = "{time} {server_name} System {system_user}:#011Delete host IP [{client_ip}] from Block List."
login = "{time} {server_name} Connection: User [{user}] from [{client_ip}] logged in successfully via [{method}]."
failed_login = "{time} {server_name} Connection: User [{user}] from [{client_ip}] failed to log in via [{method}] due to {message}"
failed_host_connection = "{time} {server_name} Connection: Host [{client_ip}] failed to connect via [{service}] due to [{message}]."
logout = "{time} {server_name} Connection: User [{user}] from [{client_ip}] logged out the server via [{method}] with totally [{data_uploaded}] uploaded and [{data_downloaded}] downloaded."
sign_in = "{time} {server_name} Connection: User [{user}] from [{client_ip}] signed in to [{service}] successfully via [{auth_method}]."
failed_sign_in = "{time} {server_name} Connection: User [{user}] from [{client_ip}] failed to sign in to [{service}] via [{auth_method}] due to authorization failure."
folder_access = "{time} {server_name} Connection: User [{user}] from [{client_ip}] via [{method}] accessed shared folder [{folder}]."
cleared_notifications = "{time} {server_name} System {system_user}:#011Cleared [{user}] all notifications successfully."
new_user = "{time} {server_name} System {system_user}:#011User [{modified_user}] was created."
deleted_user = "{time} {server_name} System {system_user}:#011System successfully deleted User [{modified_user}]."
renamed_user = "{time} {server_name} System {system_ser}:#011User [{user}] was renamed to [{modified}]."
user_app_privilege = "{time} {server_name} System {system_user}:#011The app privilege on app [{app}] for user [{user}] {message}"
user_group = "{time} {server_name} System {system_user}:#011User [{user}] was {action} the group [{group}]."
win_file_service_event = "{time} {server_name} WinFileService Event: {event}, Path: {path}, File/Folder: {file_or_folder}, Size: {size}, User: {user}, IP: {client_ip}"
configuration_export = "{time} {server_name} System {system_user}:#011System successfully exported configurations."
report_profile = "{time} {server_name} System {system_user}:#011{action} report profile named [{profile_name}]"


tasks_dict = {
    "Backup": [backup_task, "backup_task"],
    "Trigger version rotation": [backup_version_rotation, "backup_version_rotation_trigger"],
    "Version rotation": [backup_version_rotation_status, 'backup_version_rotation_status'],
    "Rotate version": [backup_rotate_version, 'backup_rotate_version'],
    "Backup task": [hyper_backup_task_message, "task_message"],
    "Scheduled Task": [scheduled_task_message, "task_message"],
    "Setting": [task_setting, "task_setting"],
    "Credentials changed": [credentials_changed, "credentials_changed"],
}

general_system_dict = {
    "automatically": [auto_install, "auto_install"],
    "back online": [back_online, "back_online"],
    "counting down": [countdown, "countdown"],
    "Download task": [download_task, "download_task"],
    "failed to convert video": [failed_video_conversion, "failed_video_conversion"],
    "link": [link_state, "link_state"],
    "Package": [package_change, "package_change"],
    "scrubbing": [scrubbing, "scrubbing"],
    "System successfully": [process_start_or_stop, "process_start_or_stop"],
    "service was": [service_started_or_stopped, "service_start_or_stop"],
    "successfully restarted": [restarted_service, "restarted_service"],
    "on battery": [on_battery, "on_battery"],
    "Update": [update, "update"],
    "shared folder": [shared_folder, "shared_folder"],
    "Shared folder": [shared_folder_application, "shared_folder_application"],
    "was enabled": [setting_enabled, "setting_enabled"],
    "unknown error": [unknown_error, "unknown_error"],
    'DNS server setting was changed': [dns_setting_changed, 'dns_setting_changed'],
    "was set to": [interface_set, 'interface_set'],
    "was changed from": [interface_changed, 'interface_changed'],
}

user_activity_dict = {
    "blocked": [blocked, "host_blocked"],
    "from Block List": [unblock, "host_unblocked"],
    "Cleared": [cleared_notifications, "cleared_notifications"],
    "failed to connect": [failed_host_connection, "failed_host_connection"],
    "failed to log in": [failed_login, "failed_login"],
    "failed to sign in": [failed_sign_in, "failed_sign_in"],
    "accessed shared folder": [folder_access, "folder_access"],
    "logged in successfully via": [login, "login"],
    "logged out the server": [logout, "logout"],
    "signed in to": [sign_in, "sign_in"],
    "was created": [new_user, "new_user"],
    "deleted": [deleted_user, "deleted_user"],
    "renamed": [renamed_user, "renamed_user"],
    "app privilege": [user_app_privilege, "user_app_privilege"],
    "group": [user_group, "user_group"],
    "WinFileService Event": [win_file_service_event, "win_file_service_event"],
    "exported configurations": [configuration_export, "configuration_export"],
    "report profile": [report_profile, "report_profile"],
}

synology_template_dict = {**tasks_dict, **general_system_dict, **user_activity_dict}


# Additional Dictionaries

synology_column_process_dict = {
    "data_uploaded": [calc_data_usage, "data_uploaded_MB"],
    "data_downloaded": [calc_data_usage, "data_download_MB"],
    "client_ip": [isolate_ip_from_parentheses, "client_ip_address"],
}

# Merging events for consolidation
synology_merge_events_dict = {
    "tasks": [value[-1] for value in tasks_dict.values()],
    "general_system": [value[-1] for value in general_system_dict.values()],
    "user_activity": [value[-1] for value in user_activity_dict.values()],
}
