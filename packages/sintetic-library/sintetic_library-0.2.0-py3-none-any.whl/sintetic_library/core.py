# Sintetic Management Client
# This module provides a client for interacting with the Sintetic GeoDB API
# with handling authentication and requests.

import requests
import json
from datetime import datetime
import pytz
from typing import Optional, Dict, Any
import uuid

# Sintetic API Endpoints
# These endpoints are used to interact with the Sintetic GeoDB API.
SINTETIC_ENDPOINTS = {
    "AUTH_LOGIN": "/auth/login",
    "STAN_FOR_D": "/stanford_attachments",
    "TREE_PROCESSORS": "/tree_processors",
    "FOREST_OPERATIONS": "/forest_operations",
    "FOREST_PROPERTIES": "/forest_properties",
   
}


class SinteticClient:
    # SinteticClient Class constructor
    def __init__(self, email: str, password: str, base_url: str = "https://api.geodb-staging.sintetic.iit.cnr.it"):
        self.base_url = base_url
        self.email = email
        self.password = password
        self.token: Optional[str] = None
        self.token_expiry: Optional[datetime] = None
        
    # Check if the token is valid    
    def _check_token_validity(self) -> bool:
        
        if not self.token or not self.token_expiry:
            return False
        
        now = datetime.now(pytz.UTC)
        return now < self.token_expiry

    # Login method to authenticate and obtain a new token
    def _login(self) -> None:
       
        login_url = f"{self.base_url}{SINTETIC_ENDPOINTS['AUTH_LOGIN']}"
        login_data = {
            "login": {
                "email": self.email,
                "password": self.password
            }
        }
        
        try:
            # Perform login request
            response = requests.post(login_url, json=login_data)
            response.raise_for_status()
            
            data = response.json()
            self.token = data["login"]["token"]
            self.token_expiry = datetime.strptime(
                data["login"]["expiry"], 
                "%Y-%m-%dT%H:%M:%SZ"
            ).replace(tzinfo=pytz.UTC)
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Exeption on: {str(e)}")
    # Get headers with authentication token
    def _get_headers(self) -> Dict[str, str]:
       
        if not self._check_token_validity():
            self._login()
        
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    # Make a generic request to the Sintetic API
    def make_request(self, method: str, endpoint: str, **kwargs) -> Any:
        """
        Perform a generic https request to the Sintetic API
        
        Args:
            method: Metodo HTTP (get, post, put, delete, etc.)
            endpoint: Endpoint of API
            **kwargs: Optional parameters for the request, such as data or params
        
        Returns:
            JSON response from the API
        """
        
        url = f"{self.base_url}{endpoint}"
        
        headers = self._get_headers()
        
        if "headers" in kwargs:
            headers.update(kwargs["headers"])
        kwargs["headers"] = headers
        
        try:
            
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            raise Exception(f"Exception on: {str(e)}")
        
    # Get Stand4D Attachments list
    # Returns:
    #     List of attachments with created_at, name and url
    def get_stan4d_list(self, **kwargs) -> Any:
        
        url = f"{self.base_url}{SINTETIC_ENDPOINTS['STAN_FOR_D']}"
        headers = self._get_headers()
        
        if "headers" in kwargs:
            headers.update(kwargs["headers"])
        kwargs["headers"] = headers
        
        try:
            method="GET"
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            
            response_data = response.json()
            #extract a subset of data composed by created_at, name and url
            filtered_data = [
                {
                    "id": item.get("id", ""),
                    "created_at": item.get("created_at", ""),
                    "name": item.get("name", ""),
                    "url": item.get("url", "")
                }
                for item in response_data
            ]
            return filtered_data
        except requests.exceptions.RequestException as e:
            raise Exception(f"Exception on: {str(e)}")
        
        
    # Get Stand4D Attachment object from given ID
    # Returns:
    #     XML object of the attachment with given ID
    def get_stan4d_file(self, fileid: str, **kwargs) -> Any:
        """
            Get Stand4D Attachment XML file from given ID
    
            Args:
                fileid: ID of the attachment to retrieve
                **kwargs: Optional parameters for the request
        
            Returns:
                str: XML content of the attachment
        """
        url = f"{self.base_url}{SINTETIC_ENDPOINTS['STAN_FOR_D']}/files/{fileid}"
        headers = self._get_headers()
        
        if "headers" in kwargs:
            headers.update(kwargs["headers"])
        kwargs["headers"] = headers
        
        try:
            method="GET"
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
        
            
            return response.text
        except requests.exceptions.RequestException as e:
            raise Exception(f"Exception on: {str(e)}")
        
    # Get Stand4D Attachment object from given ID
    # Returns:
    #     XML object of the attachment with given ID
    def save_stan4d_object(self, filename: str, xml_content: bytes, tree_processor_id: str,
            forest_operation_id: str, **kwargs) -> Any:
        """
            Get Stand4D Attachment XML file from given ID
    
            Args:
                fileid: ID of the attachment to retrieve
                **kwargs: Optional parameters for the request
        
            Returns:
                str: XML content of the attachment
        """
        url = f"{self.base_url}{SINTETIC_ENDPOINTS['STAN_FOR_D']}"
        
        data = {
            "attachment:tree_processor_id": tree_processor_id,
            "attachment:forest_operation_id": forest_operation_id,
            "attachment:id": str(uuid.uuid4())
                }
        files = {
            "attachment:file": (filename, xml_content, "application/xml")
        }

        
        headers = self._get_headers()
        headers.pop("Content-Type", None)  # requests set Content-Type for MultiPart
        
        if "headers" in kwargs:
            headers.update(kwargs["headers"])
        kwargs["headers"] = headers
        # --- STAMPA DETTAGLI DELLA CHIAMATA ---
        if kwargs:
            print("Altri kwargs:", kwargs)
        try:
            response = requests.post(
                url,
                data=data,
                files=files,
                **kwargs
            )
            response.raise_for_status()      
            return response
 
        except requests.exceptions.RequestException as e:
            raise Exception(f"Exception on: {str(e)}")
        
        
    # Get list forest operations
    # Returns:
    #       json array of forest operations with created_at, name and url
    def get_list_forest_operations(self, **kwargs) -> Any:
        """
            Get list of forest operations
            
            Args:
                **kwargs: Optional parameters for the request
        
            Returns:
                List of forest operations with created_at, name and url
        """
        url = f"{self.base_url}{SINTETIC_ENDPOINTS['FOREST_OPERATIONS']}"
        headers = self._get_headers()
        
        if "headers" in kwargs:
            headers.update(kwargs["headers"])
        kwargs["headers"] = headers
        
        try:
            method="GET"
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
        
            
            return response.text
        except requests.exceptions.RequestException as e:
            raise Exception(f"Exception on: {str(e)}")
    
    # Get list forest properties
    def get_list_forest_properties(self, **kwargs) -> Any:
        """
            Get list of forest properties
            Args:
                **kwargs: Optional parameters for the request
            Returns:
                List of forest properties with created_at, name and url
        """
        url = f"{self.base_url}{SINTETIC_ENDPOINTS['FOREST_PROPERTIES']}"
        headers = self._get_headers()
        
        if "headers" in kwargs:
            headers.update(kwargs["headers"])
        kwargs["headers"] = headers
        
        try:
            method="GET"
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
        
            
            return response.text
        except requests.exceptions.RequestException as e:
            raise Exception(f"Exception on: {str(e)}")
    
    
    # Get list tree processors
    # Returns:
    #     json array of tree processors with created_at, name and url
    def get_list_tree_processors(self, **kwargs) -> Any:
        """
            Get list of tree processors
            
            Args:
                **kwargs: Optional parameters for the request
        
            Returns:
                List of tree processors with created_at, name and url
        """
        url = f"{self.base_url}{SINTETIC_ENDPOINTS['TREE_PROCESSORS']}"
        headers = self._get_headers()
        
        if "headers" in kwargs:
            headers.update(kwargs["headers"])
        kwargs["headers"] = headers
        
        try:
            method="GET"
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
        
            
            return response.text
        except requests.exceptions.RequestException as e:
            raise Exception(f"Exception on: {str(e)}")
        
        
    # Create a new tree processor
    def create_tree_processor(self, data: dict, **kwargs) -> Any:
        """
        Create a new tree processor
        Args:
            data: Dictionary containing the tree processor data
            **kwargs: Optional parameters for the request
        Returns:
            JSON response from the API
        """
        
        # Generate a unique ID for the tree processor
        data["id"] = str(uuid.uuid4())
        url = f"{self.base_url}{SINTETIC_ENDPOINTS['TREE_PROCESSORS']}"
        headers = self._get_headers()
        headers["Content-Type"] = "application/json"
        
        try:
            response = requests.post(
                url=url,
                headers=headers,
                json=data  # requests gestirà automaticamente la serializzazione in JSON
            )
            
            response.raise_for_status()
            return data["id"]
        except requests.exceptions.RequestException as e:
            raise Exception(f"Exception on: {str(e)}")
    
    
    # Create a new forest operation
    def create_forest_operation(self, data: dict, **kwargs) -> Any:
        """
        Create a new forest operation
        Args:
            data: Dictionary containing the forest operation data
            **kwargs: Optional parameters for the request
        Returns:
            JSON response from the API
        """
        
        url = f"{self.base_url}{SINTETIC_ENDPOINTS['FOREST_OPERATIONS']}"
        headers = self._get_headers()
        headers["Content-Type"] = "application/json"
        data["id"] = str(uuid.uuid4())
        print("Data to create forest operation:", data)
        try:
            response = requests.post(
                url=url,
                headers=headers,
                json=data  # requests gestirà automaticamente la serializzazione in JSON
            )
            
            response.raise_for_status()
            return data["id"]
        except requests.exceptions.RequestException as e:
            raise Exception(f"Exception on: {str(e)}")    
        
        
    # Delete a new tree processor
    def delete_stan4d_file(self, fileid: str, **kwargs) -> Any:
       
        """        Delete a Stand4D file by its ID
        Args:
            fileid: ID of the Stand4D file to delete
            **kwargs: Optional parameters for the request
        Returns:
            int: HTTP status code of the response
        """
        
        url = f"{self.base_url}{SINTETIC_ENDPOINTS['STAN_FOR_D']}/{fileid}"
        headers = self._get_headers()
        headers["Content-Type"] = "application/json"
        
        try:
            response = requests.delete(
                url=url,
                headers=headers,
                
            )
            
            response.raise_for_status()
            return response.status_code
        except requests.exceptions.RequestException as e:
            raise Exception(f"Exception on: {str(e)}")
        
    
    # Delete a forest operation
    # Args:
    #       forest_operation_id: ID of the forest operation to delete
    # Returns:
    #       int: HTTP status code of the response
    def delete_forest_operation(self, forest_operation_id: str, **kwargs) -> Any:
        
        url = f"{SINTETIC_ENDPOINTS['FOREST_OPERATIONS']}/{forest_operation_id}"
        headers = self._get_headers()
        
        if "headers" in kwargs:
            headers.update(kwargs["headers"])
        kwargs["headers"] = headers
        
        try:
            
            response = self.make_request("DELETE", url, **kwargs)
            
            return response.status_code
        except requests.exceptions.RequestException as e:
            raise Exception(f"Exception on: {str(e)}")
    
    # Delete a tree processor
    # Args:
    #       forest_operation_id: ID of the forest operation to delete
    # Returns:
    #       int: HTTP status code of the response
    def delete_tree_processor(self, tree_processor_id: str, **kwargs) -> Any:
        """
            Get list of forest operations
            
            Args:
                **kwargs: Optional parameters for the request
        
            Returns:
                List of forest operations with created_at, name and url
        """
        url = f"{SINTETIC_ENDPOINTS['TREE_PROCESSORS']}/{tree_processor_id}"
        headers = self._get_headers()
        
        if "headers" in kwargs:
            headers.update(kwargs["headers"])
        kwargs["headers"] = headers
        
        try:
            response = self.make_request("DELETE", url, **kwargs)
            
            return response.status_code
        except requests.exceptions.RequestException as e:
            raise Exception(f"Exception on: {str(e)}")
    