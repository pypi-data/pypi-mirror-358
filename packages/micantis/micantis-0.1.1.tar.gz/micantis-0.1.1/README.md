# Micantis API Wrapper

A lightweight Python wrapper for interacting with the Micantis API plus some helpful utilities.  
Built for ease of use, fast prototyping, and clean integration into data workflows.

---

## 🚀 Features

- Authenticate and connect to the Micantis API service
- Download and parse csvs and binary data into pandas DataFrames
- Filter, search, and retrieve metadata
- Utility functions to simplify common API tasks

---

## ⚠️ Important

This package is designed for authenticated Micantis customers only.  
If you are not a Micantis customer, the API wrapper and utilities in this package will not work for you.

For more information on accessing the Micantis API, please contact us at info@micantis.io.

---

## 📦 Installation

```pip install micantis ```

---

## 💻 Examples

### Import functions

``` python
import pandas as pd
from micantis import MicantisAPI
```

### Initialize API

``` python
# Option 1 - login with username and password
service_url = 'your service url'
username = 'your username'
password = 'your password'

api = MicantisAPI(service_url=service_url, username=username, password=password)
```

``` python
# Option 2 - login in with Microsoft Entra ID
SERVICE = 'your service url'
CLIENT_ID = 'your client id'
AUTHORITY = 'https://login.microsoftonline.com/organizations'
SCOPES = ['your scopes']

api = MicantisAPI(service_url=SERVICE, client_id=CLIENT_ID, authority=AUTHORITY, scopes=SCOPES)
```
### Authenticate API
``` api.authenticate() ```

### Download Data Table Summary

#### Optional parameters
- `search`: Search string (same syntax as the Micantis WebApp)
- `barcode`: Search for a specific barcode
- `limit`: Number of results to return (default: 500)
- `min_date`: Only return results after this date
- `max_date`: Only return results before this date
- `show_ignored`: Include soft-deleted files (default: `True`)

```python
table = api.get_data_table(search=search, barcode=barcode, min_date=min_date, max_date=max_date, limit = 10, show_ignored=show_ignored)
table
```

### Download Binary Files

``` python
# Download single file

file_id = 'File ID obtained from data table, id column'
df = api.download_binary_file(id)

```

``` python
# Download many files using list of files from the table

file_id_list = table['id'].to_list()
data = []

for id in file_id_list:
    df = api.download_csv_file(id)
    data.append(df)

all_data = pd.concat(data)
```

### Download CSV Files

``` python
# Download single file

file_id = 'File ID obtained from data table, id column'
df = api.download_csv_file(id)
```

``` python
# Download multiple files

id_list = table['id'].to_list()
data = []

for id in id_list:
    df = api.download_csv_file(id)
    data.append(df)

all_data = pd.concat(data)
```
## Cells Table
### Download Cell ID Information
Retrieve a list of cell names and GUIDs from the Micantis database with flexible filtering options.

#### Optional parameters
- `search`: Search string (same syntax as the Micantis WebApp)
- `barcode`: Search for a specific barcode
- `limit`: Number of results to return (default: 500)
- `min_date`: Only return results after this date
- `max_date`: Only return results before this date
- `show_ignored`: Include soft-deleted files (default: `True`)

``` python
search = "*NPD*"
cells_df = api.get_cells_list(search=search)
cells_df.head()
```
### Download Cell Metadata

``` python
# Download many files using list of files from the table

cell_id_list = cells_df['id'].to_list()

cells_metadata = api.get_cell_metadata(cell_ids = cell_id_list)
```

