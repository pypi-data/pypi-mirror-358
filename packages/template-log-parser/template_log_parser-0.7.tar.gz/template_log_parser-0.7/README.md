# template-log-parser : Log Files into Tabular Data
---
`template-log-parser` is designed to streamline the log analysis process by pulling relevant information into DataFrame columns by way of user designed templates.  `parse` and `pandas` perform the heavy lifting. Full credit to those well-designed projects.

This project offers some flexibility in how you can process your log files.  You can utilize built-in template functions (Kodi, Omada Controller, Open Media Vault, PFSense, PiHole, Synology DSM, and Ubuntu) or build your own workflow. 

#### Getting Started
---

```bash
pip install template-log-parser
```

The foundational principle in this project is designing templates that fit repetitive log file formats.

Example log line:
```bash
my_line = '2024-06-13T15:09:35 server_15 login_authentication[12345] rejected login from user[user_1].'
```
    
Example template:
```bash
template = '{time} {server_name} {service_process}[{service_id}] {result} login from user[{username}].'
```

The words within the braces will eventually become column names in a DataFrame.  You can capture as much or as little data from the line as you see fit.  For instance, you could opt to omit {result} from the template and thus look to match only rejected logins for this example.

Note that templates will be looking for an exact match.  Items such as timestamps, time elapsed, and data usage should be captured as they are unique to that log line instance.

#### Template Dictionaries
---
After creating templates, they should be added to a dictionary with the following format:
```bash
ex_dict = {'search_string': [template_name, 'event_type'], ...}
```
- 'search_string' is text expected to be found in the log file line.  The parsing function will only check the template against the line if the text is present.
- template_name is the user defined template.
- 'event_type' is an arbitrary string name assigned to this type of occurrence.

Using the example template:
```bash
my_template_dict = {'login from': [template, 'login_attempt'], ...}
```

#### Basic Usage Examples
---
Parse a single event:
```bash
from template_log_parser import parse_function

event_type, parsed_info = parse_function(my_line, my_template_dict)

print(event_type)
'login_attempt' 

print(parsed_info)
    {
    'time': '2024-06-13T15:09:35',
    'server_name': 'server_15',
    'service_process': 'login_authentication', 
    'service_id': '12345',
    'result': 'rejected',
    'username': 'user_1'
    }
```
Parse an entire log file and return a Pandas DataFrame:
```bash
from template_log_parser import log_pre_process

df = log_pre_process('log_file.log', my_template_dict)

print(df.columns)
Index(['time', 'server_name', 'service_process', 'service_id', 'result', 'username', 'event_type', 'event_data'])
```
This is just a tabular data form of many single parsed events.
 - event_type column value is determined based on the matching template
 - event_data column holds the raw string data for each log line
 - Essentially, each key from the parsed_info dictionary will become its own column populated with the associated value.
 
Note: 
Events that do not match a template will be returned as event_type ('Other') with column: ('Unparsed_text').

#### Granular Log Processing
---
By default, this procedure returns a dictionary of Pandas DataFrames, formatted as {'event_type': df}.

```bash
from template_log_parser import process_log

my_df_dict = process_log('log_file.log', my_template_dict)

print(my_df_dict.keys())
dict_keys(['login_attempt', 'event_type_2', 'event_type_3', ...])
```

Alternatively as one large DataFrame:
```bash
from template_log_parser import process_log

my_df = process_log('log_file.log', my_template_dict, dict_format=False)

print(my_df.columns)
Index(['event_type', 'time', 'server_name', 'service_process', 'service_id', 'result', 'username'])
```

Filter results using match to ensure that log lines contain the desired strings, or eliminate to ensure to remove lines with strings deemed superfluous. 
```bash
from template_log_parser import process_log

my_matched_df = process_log('log_file.log', my_template_dict, match=['error', 'login'] , dict_format=False)
my_eliminated_df = process_log('log_file.log', my_template_dict, eliminate=['user: admin', 'success'], match_type='all' , dict_format=False)

```

###### Some Notes
---
- By default `drop_columns=True` instructs `process_log()` to discard 'event_data' along with any other columns modified by column functions (SEE NEXT).
- (OPTIONAL ARGUMENT) `additional_column_functions` allows user to apply functions to specific columns.  These functions will create a new column, or multiple columns if so specified.  The original column will be deleted if `drop_columns=True`.  This argument takes a dictionary formatted as:
```bash
add_col_func = {column_to_run_function_on: [function, new_column_name_OR_list_of_new_colum_names]}
 ```
- (OPTIONAL ARGUMENT) `merge_dictionary` allows user to concatenate DataFrames that are deemed to be related.  Original DataFrames will be discarded, and the newly merged DF will be available within the dictionary by its new key.  when `dict_format=False`, this argument has no effect.  This argument takes a dictionary formatted as:
```bash
my_merge_dict = {'new_df_key': [df_1_key, df_2_key, ...], ...}
```
- (OPTIONAL ARGUMENT) `datetime_columns` takes a list of columns that should be converted using `pd.to_datetime()`
- (OPTIONAL ARGUMENT) `localize_time_columns` takes a list of columns whose timezone should be eliminated (column must also be included in the `datetime_columns` argument).
---
#### Built-Ins
This project includes log process functions for Kodi, Omada Controller, Open Media Vault, PFSense, PiHole, Synology DSM, and Ubuntu. These are still being actively developed as not all event types have been accounted for.
As a general philosophy, this project aims to find middle ground between useful categorization of log events and sheer number of templates.

Submissions for improvement are welcome.

Notes: 

- PFSense templates match (RFC 5424, with RFC 3339 microsecond precision time stamps)
- Synology templates match (BSD, RFC 3164)
```bash
from template_log_parser.built_ins import built_in_process_log

my_kodi_log_dict = built_in_process_log(built_in='kodi', file='my_omada_file.log')

my_omada_log_dict = built_in_process_log(built_in='omada', file='my_omada_file.log')

my_omv_log_dict = built_in_process_log(built_in='omv', file='my_omv_file.log')

my_pfsense_log_dict = built_in_process_log(built_in='pfsense', file='my_pfsense_file.log')

my_synology_log_dict = built_in_process_log(built_in='synology', file='my_synology_log.log')

my_ubuntu_log_dict = built_in_process_log(built_in='ubuntu', file='my_ubuntu_log.log')
```

PiHole templates will likely require modification to fit the use case.  PiHole does not natively output remote logs.  
In many cases, additional prefixing information will be present from third parties.  This should be added as needed.

```bash
from template_log_parser.log_type_classes import pihole
from template_log_parser.built_ins import built_in_process_log

# Modify the built-in templates
# Your logfile might have zero width no break space present which can prevent template matches
pihole.templates = {
        search_term: 
        ["{utc_timestamp} {hostname} - " + template, event_type] for search_term, (template, expected_items, event_type) in pihole.templates.items()
}

my_pihole_log_dict = built_in_process_log(built_in='pihole', file='my_pihole_log.log')

```

As Open Media Vault and Ubuntu are based on Debian, their templates are combined with a Debian template dictionary.  
This can be used separately if desired. 
At present, the template dictionary for Debian events is very spartan; it serves as only a cursory classification mechanism. 

```bash
my_debian_log_dict = built_in_process_log(built_in='debian', file='my_debian_log.log')
```

## DISCLAIMER

**This project is in no way affiliated with the products mentioned (Debian, Kodi, Omada, Open Media Vault, PFSense, PiHole, Synology, or Ubuntu).
Any usage of their services is subject to their respective terms of use.**
