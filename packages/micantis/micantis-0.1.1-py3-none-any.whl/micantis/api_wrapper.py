import requests
import pandas as pd
from .utils import binary_to_dataframe
import io
from msal import PublicClientApplication
import fnmatch

class MicantisAPI:
    """
    A client for interacting with the Micantis API.

    Supports authentication via Micantis credentials or Microsoft Entra ID.
    Enables downloading CSV/binary data and querying file metadata.

    """
        
    def __init__(self, service_url, username=None, password=None, client_id=None, authority=None, scopes=None):
        """
        Initialize the API client.

        Parameters
        ----------
        service_url : str
            Base URL for the Micantis API.
        username : str, optional
            Username for login-based authentication.
        password : str, optional
            Password for login-based authentication.
        client_id : str, optional
            Microsoft Entra client ID.
        authority : str, optional
            Microsoft Entra authority URL.
        scopes : list of str, optional
            OAuth scopes for Microsoft Entra authentication.
        """

        self.service_url:str = service_url.rstrip("/")
        self.username:str = username
        self.password:str = password
        self.client_id:str = client_id
        self.authority:str = authority
        self.scopes:str = scopes or ["user.read"]  # Default scope
        self.token:str = None
        self.headers:str = None
    
    def authenticate_via_login(self):
        """
        Authenticates with the Micantis API using username and password.
        Sets the authorization header if successful.
        """

        try:
            response = requests.post(f"{self.service_url}/api/authenticate/login",json={"username": self.username, "password": self.password})
            response.raise_for_status()  # Raise an error for bad status codes
            self.token = response.json()["token"]
            if not self.token:
                raise ValueError("Authentication failed: Token not found in response.")
            self.headers = {"Authorization": f"Bearer {self.token}"}
            print("✅ Authentication via login successful!")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Authentication request failed: {e}")
    
    def authenticate_via_entra(self):
        """
        Authenticates with Microsoft Entra using MSAL's interactive login.
        Sets the authorization header if successful.
        """
                
        try:
            app = PublicClientApplication(self.client_id, authority=self.authority)
            result = app.acquire_token_interactive(self.scopes)
            if 'access_token' in result:
                token = result['access_token']
                self.headers = {'Authorization': f'Bearer {token}'}
                print("✅ Authentication via Entra successful!")
            else:
                error = result['error']
                rv = error
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Authentication request failed: {e}") 
        
    
    def authenticate(self):
        """
        Automatically selects authentication method:
        - Uses Entra if `client_id`, `authority`, and `scopes` are provided.
        - Falls back to login if `username` and `password` are provided.
        """
        if all([self.client_id, self.authority, self.scopes]):
            self.authenticate_via_entra()
        elif all([self.username, self.password]):
            self.authenticate_via_login()
        else:
            raise ValueError("Insufficient credentials: Provide either (username & password) or (client_id, authority & scopes)")

    
    def get_data_table(
        self,
        offset: int=0,
        barcode: str=None,
        search: str=None,
        min_date=None,
        max_date=None,
        show_ignored: bool=True,
        limit: int = 500
    ):
        """
        Fetches data table with optional filters and returns it as a Pandas DataFrame.
        
        :param offset: Pagination offset.
        :param barcode: Barcode filter (optional).
        :param search: Search text filter (optional).
        :param min_date: Minimum date filter (ISO format) (optional).
        :param max_date: Maximum date filter (ISO format) (optional).
        :param show_ignored: Whether to include soft deleted items (default: True).
        :return: Pandas DataFrame of the fetched data.
        """
        if not self.headers:
            raise RuntimeError("Authentication required. Call authenticate() first.")

        # Build query parameters dynamically
        params = {
            "offset": offset,
            "showIgnored": str(show_ignored).lower(),
            "limit": limit
        }

        filter_index = 0
        if min_date or max_date:
            params[f"filters[{filter_index}].specialColumn"] = 4
            if min_date:
                params[f"filters[{filter_index}].minDate]"] = min_date
            if max_date:
                params[f"filters[{filter_index}].maxDate]"] = max_date
            filter_index += 1

        if barcode:
            params[f"filters[{filter_index}].specialColumn"] = 27
            params[f"filters[{filter_index}].searchText"] = barcode
            filter_index += 1

        if search:
            params["search"] = search

        try:
            # Make the GET request
            response = requests.get(
                f"{self.service_url}/publicapi/v1/data/list",
                headers=self.headers,
                params=params,
            )
            response.raise_for_status()

            # Parse response JSON
            items = response.json().get("items", [])
            if not items:
                print("⚠️ No data returned.")
                return pd.DataFrame()

            # Convert to DataFrame
            return pd.DataFrame(items)

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"GET request failed: {e}")
        
    def download_csv_file(self, guid: str) -> pd.DataFrame:
        """
            Download a CSV file from the API and convert it to a pandas DataFrame.

            Parameters:
            -----------
            guid : str
                The unique identifier (GUID) of the file to be downloaded.

            Raises:
            -------
            RuntimeError
                - If the user is not authenticated (missing `self.headers`).
                - If the GET request fails due to a network error or invalid URL.
            
            Returns:
            --------
            pd.DataFrame or None
                - A pandas DataFrame containing the data from the CSV file if the download is successful.
                - Returns `None` if no data is returned or if the CSV file is empty.

            Example Usage:
            --------------
            client.authenticate(api_key="myapikey")
            df = client.download_csv_file(guid="12345-abcde-67890")
            if df is not None:
                print(df.head())
            else:
                print("No data returned.")
        """
        if not self.headers:
            raise RuntimeError("Authentication required. Call authenticate() first.")
        
        try:
            r = requests.get(f'{self.service_url}/publicapi/v1/download/fullcsv/{guid}', headers=self.headers)
            try:
                buffer = io.BytesIO(r.content)
                df = pd.read_csv(buffer)
                return df
            except: 
                print("⚠️ No data returned.")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"GET request failed: {e}")
        
    def get_metadata(self, guid: str) -> dict:
        """
        Fetch metadata for a given data file.

        Parameters
        ----------
        guid : str
            Unique identifier for the file.

        Returns
        -------
        dict
            Metadata associated with the file.
        """
        if not self.headers:
            raise RuntimeError("Authentication required. Call authenticate() first.")
        try:
            r = requests.get(f"{self.service_url}/publicapi/v1/data/getmetadata/{guid}", headers = self.headers)
            return r.json()

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"GET request failed: {e}")
        
    def download_binary_file(self, guid: str) -> pd.DataFrame:
        """
        Download a binary file, decode it using its metadata, and return a DataFrame.

        Parameters
        ----------
        guid : str
            File ID from the data table.

        Returns
        -------
        pd.DataFrame
            Parsed binary data as a DataFrame.
        """

        if not self.headers:
            raise RuntimeError("Authentication required. Call authenticate() first.")
        try:
            r = requests.get(f"{self.service_url}/publicapi/v1/download/binary/{guid}", headers = self.headers)
            try:
                json = self.get_metadata(guid)
                aux_names = [f"{entry['name']} ({entry['units']})" for entry in json.get('auxiliaryData', [])]
                df = binary_to_dataframe(r.content, aux_names=aux_names)
                return df
            except:
                print("⚠️ No data returned.")
        
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"GET request failed: {e}")
        
    def get_cells_list(
        self,
        offset: int=0,
        barcode: str=None,
        search: str=None,
        min_date=None,
        max_date=None,
        show_ignored: bool=True,
        limit: int = 500
    ):
        """
        Fetches cells table list with optional filters and returns it as a Pandas DataFrame.
        
        :param offset: Pagination offset.
        :param barcode: Barcode filter (optional).
        :param search: Search text filter (optional).
        :param min_date: Minimum date filter (ISO format) (optional).
        :param max_date: Maximum date filter (ISO format) (optional).
        :param show_ignored: Whether to include soft deleted items (default: True).
        :return: Pandas DataFrame of the fetched data.
        """
        if not self.headers:
            raise RuntimeError("Authentication required. Call authenticate() first.")

        # Build query parameters dynamically
        params = {
            "offset": offset,
            "showIgnored": str(show_ignored).lower(),
            "limit": limit
        }

        filter_index = 0
        if min_date or max_date:
            params[f"filters[{filter_index}].specialColumn"] = 4
            if min_date:
                params[f"filters[{filter_index}].minDate]"] = min_date
            if max_date:
                params[f"filters[{filter_index}].maxDate]"] = max_date
            filter_index += 1

        if barcode:
            params[f"filters[{filter_index}].specialColumn"] = 27
            params[f"filters[{filter_index}].searchText"] = barcode
            filter_index += 1

        if search:
            params["search"] = search

        try:
            # Make the GET request
            response = requests.get(
                f"{self.service_url}/publicapi/v1/cells/list",
                headers=self.headers,
                params=params,
            )
            response.raise_for_status()

            # Parse response JSON
            items = response.json().get("items", [])
            if not items:
                print("⚠️ No data returned.")
                return pd.DataFrame()

            # Convert to DataFrame
            return pd.DataFrame(items)

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"GET request failed: {e}")

    def list_cell_metadata_definitions(self, type='df'):
        """ 
        Returns a list of cell metadata types
        """
        if not self.headers:
                raise RuntimeError("Authentication required. Call authenticate() first.")
        try:
            # Make the GET request
            response = requests.get(
                f"{self.service_url}/publicapi/v1/metadata/list/cells",
                headers=self.headers,
            )

            item = response.json()
            if type == 'df':
                df = pd.DataFrame(item)
                return df
            
            else:
                return item

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"GET request failed: {e}")
        
    def get_cell_metadata(self, cell_ids: list):
        """
        Fetch metadata for specific cells, with optional filtering by property names and kind.

        Parameters
        ----------
        cell_ids : list of str
            List of cell IDs to fetch metadata for.

        Returns
        -------
        pd.DataFrame
            Metadata results per cell in wide format.
        """
        if not self.headers:
            raise RuntimeError("Authentication required. Call authenticate() first.")
        
        if not isinstance(cell_ids, list) or not cell_ids:
            raise ValueError("cell_ids must be a non-empty list of Cell IDs.")
        
        # Default to all metadata if no properties specified
        property_definition_ids = []

        # Build request payload
        payload = {
            "cellTestIds": cell_ids,
            "propertyDefinitionIds": property_definition_ids
        }

        try:
            response = requests.post(
                f"{self.service_url}/publicapi/v1/cells/getmetadata",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()

            items = response.json().get("items", [])
            
            rows = []
            for item in items:
                row = {'id': item['id']}
                for prop in item['userProperties']:
                    row[prop['name']] = prop['value']
                rows.append(row)

            df = pd.DataFrame(rows)
            return df

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"POST request failed: {e}")

        






            
            
