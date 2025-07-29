
id_process = "{time} {server_name} {process}[{id}]: {message}"
kernel = "{time} {server_name} kernel: {message}"
pam_unix = "{time} {server_name} {process}: pam_unix({session}): {message}"
mtp_probe = "{time} {server_name} mtp-probe: {message}"
rsync = "{time} {server_name} rsync-{id} {message}"
rsyslogd = "{time} {server_name} rsyslogd: {message}"
sudo = "{time} {server_name} sudo: {message}"
upssched_cmd = "{time} {server_name} upssched-cmd: {message}"


debian_template_dict = {
    "]:": [id_process, "id_process"],
    "kernel": [kernel, "kernel"],
    'pam_unix': [pam_unix, 'pam_unix'],
    'sudo': [sudo, 'sudo'],
    "rsync": [rsync, "rsync"],
    'rsyslogd': [rsyslogd, 'rsyslogd'],
    'upssched-cmd': [upssched_cmd, 'upssched-cmd'],
    'mtp-probe': [mtp_probe, 'mtp_probe']
}