# Base templates for Pihole log analysis

# pihole
dnsmasq_cached = "{time} dnsmasq[{id}]: cached {query} is {cached_resolved_ip}"
dnsmasq_cached_stale = "{time} dnsmasq[{id}]: cached-stale {query} is {cached_resolved_ip}"
dnsmasq_compile = "{time} dnsmasq[{id}]: compile time options: {message}"
dnsmasq_config = "{time} dnsmasq[{id}]: config {host} is {result}"
dnsmasq_custom_list = '{time} dnsmasq[{id}]: /etc/pihole/hosts/custom.list {host_ip} is {host_name}'
dnsmasq_domain = "{time} dnsmasq[{id}]: {type} domain {query} is {result}"
dnsmasq_exactly_blacklisted = "{time} dnsmasq[{id}]: exactly blacklisted {query} is {result}"
dnsmasq_exactly_denied = "{time} dnsmasq[{id}]: exactly denied {query} is {result}"
dnsmasq_exiting = "{time} dnsmasq[{id}]: exiting on receipt of SIGTERM"
dnsmasq_forward = "{time} dnsmasq[{id}]: forwarded {query} to {dns_server}"
dnsmasq_gravity_blocked = "{time} dnsmasq[{id}]: gravity blocked {query} is {result}"
dnsmasq_host_name_resolution = "{time} dnsmasq[{id}]: /etc/hosts {host_ip} is {host_name}"
dnsmasq_host_name = "{time} dnsmasq[{id}]: Pi-hole hostname {host_name} is {host_ip}"
dnsmasq_inotify = "{time} dnsmasq[{id}]: inotify: {message}"
dnsmasq_locally_known = "{time} dnsmasq[{id}]: using only locally-known addresses for {result}"
dnsmasq_query = "{time} dnsmasq[{id}]: query[{query_type}] {destination} from {client}"
dnsmasq_rate_limiting = "{time} dnsmasq[{id}]: Rate-limiting {query} is {message}"
dnsmasq_read = "{time} dnsmasq[{id}]: read {path} - {names} names"
dnsmasq_reply = "{time} dnsmasq[{id}]: reply {query} is {resolved_ip}"
dnsmasq_reply_truncated = "{time} dnsmasq[{id}]: reply is truncated"
dnsmasq_started = "{time} dnsmasq[{id}]: started, version {version} cachesize {cachesize}"
dnsmasq_using_nameserver = "{time} dnsmasq[{id}]: using nameserver {nameserver_ip}#53"
dnsmasq_using_nameserver_domain = "{time} dnsmasq[{id}]: using nameserver {nameserver_ip}#53 for domain {domain}"

# ftl
ftl_info = "{time} [{ids}] INFO: {message}"
ftl_warning = "{time} [{ids}] WARNING: {message}"

# webserver
webserver_initializing_http_server = '[{time}] Initializing HTTP server on ports "{ports}"'
webserver_authentication_required = '[{time}] Authentication required, redirecting to {redirect}'

# Gravity
gravity = '{trim}[{result}]{message}'

pihole = {
    "query": [dnsmasq_query, "dnsmasq_query"],
    "reply": [dnsmasq_reply, "dnsmasq_reply"],
    "cached": [dnsmasq_cached, "dnsmasq_cached"],
    "cached-stale": [dnsmasq_cached_stale, "dnsmasq_cached_stale"],
    "forwarded": [dnsmasq_forward, "dnsmasq_forward"],
    "gravity blocked": [dnsmasq_gravity_blocked, "dnsmasq_gravity_blocked"],
    "exactly denied": [dnsmasq_exactly_denied, "dnsmasq_exact_denied"],
    "domain": [dnsmasq_domain, "dnsmasq_domain"],
    "hostname": [dnsmasq_host_name, "dnsmasq_hostname_resolution"],
    "config": [dnsmasq_config, "dnsmasq_config"],
    "compile time options": [dnsmasq_compile, "dnsmasq_compile_time_options"],
    "exactly blacklisted": [dnsmasq_exactly_blacklisted, "dnsmasq_exact_blacklist"],
    "exiting on receipt of SIGTERM": [dnsmasq_exiting, "dnsmasq_exiting_sigterm"],
    "hosts": [dnsmasq_host_name_resolution, "dnsmasq_hostname_resolution"],
    "locally-known": [dnsmasq_locally_known, "dnsmasq_locally_known"],
    "Rate-limiting": [dnsmasq_rate_limiting, "dnsmasq_rate_limiting"],
    "read ": [dnsmasq_read, "dnsmasq_read"],
    "reply is truncated": [dnsmasq_reply_truncated, "dnsmasq_reply_truncated"],
    "started": [dnsmasq_started, "dnsmasq_started"],
    'inotify': [dnsmasq_inotify, 'dsnmasq_inotify'],
    'using nameserver': [dnsmasq_using_nameserver, 'dnsmasq_using_nameserver'],
    ' using nameserver': [dnsmasq_using_nameserver_domain, 'dnsmasq_using_nameserver_domain'],
    "custom.list": [dnsmasq_custom_list, 'dnsmasq_custom_list'],
}

ftl = {
    'INFO': [ftl_info, 'ftl_info'],
    'WARNING': [ftl_warning, 'ftl_warning'],
}

webserver = {
    'Initializing HTTP server': [webserver_initializing_http_server, 'webserver_initializing_server'],
    'Authentication required': [webserver_authentication_required, 'webserver_authentication_required'],
}

gravity = {
    '[i]': [gravity, 'gravity_message'],
    '[✓]' : [gravity, 'gravity_message'],
}

pihole_template_dict = {**pihole, **ftl, **webserver, **gravity}


# Merging events for consolidation
pihole_merge_events_dict = {
    "pihole": [value[-1] for value in pihole.values()],
    "ftl": [value[-1] for value in ftl.values()],
    'webserver': [value[-1] for value in webserver.values()],
    'gravity': [value[-1] for value in gravity.values()]
}
