from template_log_parser.templates.debian_templates import debian_template_dict

apt_daemon = "{time} {server_name} {process}: {level}: {message}"
dbus_daemon = '{time} {server_name} dbus-daemon: {message}'
desktop = "{time} {server_name} {process}.des {message}"
desktop_2 = "{time} {server_name} {process}.desktop{message}"
desktop_3 = "{time} {server_name} {process}.deskto{message}"
gdm = "{time} {server_name} gdm{process}: {action}: {message}"
package_kit = "{time} {server_name} PackageKit: {message}"
pycharm = "{time} {server_name} pycharm-{process} {message}"
snapd = "{time} {server_name} {process}.snapd- {message}"
sticky_notes = "{time} {server_name} sticky-notes-simple_sticky-notes{message}"
ubuntu = "{time} {server_name} ubuntu-{process} {message}"
vsce_sign = '{time} {server_name} vsce-sign: {message}'

ubuntu_templates = {
    ".des": [desktop, "desktop"],
    ".desktop": [desktop_2, "desktop"],
    ".deskto": [desktop_3, 'desktop'],
    "PackageKit": [package_kit, 'package_kit'],
    "pycharm": [pycharm, "pycharm"],
    'gdm': [gdm, 'gdm'],
    'ubuntu': [ubuntu, 'ubuntu'],
    'sticky-notes-simple_sticky-notes': [sticky_notes, 'sticky_notes'],
    'dbus-daemon': [dbus_daemon, 'dbus_daemon'],
    'AptDaemon': [apt_daemon, 'apt_daemon'],
    'snapd': [snapd, 'snapd'],
    'vsce-sign': [vsce_sign, 'vsce_sign']

}

ubuntu_template_dict = {
    **ubuntu_templates,
    **debian_template_dict
}

ubuntu_column_process_dict = {}
ubuntu_merge_events_dict = {}