from template_log_parser.templates.debian_templates import debian_template_dict

openmediavault_id_process = "{time} {server_name} openmediavault-{process}[{id}]: {message}"
openmediavault_process = "{time} {server_name} openmediavault-{process} {message}"
omv_id_process = "{time} {server_name} omv-{process}[{id}]:{message}"
omv_process = "{time} {server_name} omv-{process}: {message}"
conf = "{time} {server_name} conf_{version}: {message}"
php = "{time} {server_name} php{version}: {action}: {message}"

omv_process_dict = {
    " omv-": [omv_id_process, "omv_id_process"],
    "omv-": [omv_process, "omv_process"],
}

openmediavault_process_dict = {
    " openmediavault-": [openmediavault_id_process, "openmediavault_id_process"],
    "openmediavault-": [openmediavault_process, "openmediavault_process"],
}

omv_other_events = {
    "conf_": [conf, "conf"],
    "php": [php, 'php'],
}

# OMV often runs on debian, so it makes sense to use templates from that dictionary rather than create new ones
omv_template_dict = {
    **omv_process_dict,
    **openmediavault_process_dict,
    **omv_other_events,
    **debian_template_dict,
}

omv_merge_events_dict = {
    "omv": [value[-1] for value in omv_process_dict.values()],
    "openmediavault": [value[-1] for value in openmediavault_process_dict.values()],
}
