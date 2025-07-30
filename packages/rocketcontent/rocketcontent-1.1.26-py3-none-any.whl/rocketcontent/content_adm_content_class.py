import json
import requests
import urllib3
import warnings
from dataclasses import dataclass
from typing import Optional
from copy import deepcopy
from .content_config import ContentConfig
from urllib.parse import quote
import time

# Disable https warnings if the http certificate is not valid
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

class ContentAdmContentClass:
    """
    ContentAdmContentClass provides functionality to manage content class definitions for a repository administration system.
    Classes:
        ContentClass: A data class representing the configuration and properties of a content class, including options for compression, encryption, retention, indexing, and more.
    Methods:
        __init__(content_config):
            Initializes the ContentAdmContentClass with a ContentConfig object, setting up repository admin URL, logger, and headers.
        create_content_class(content_class_json):
            Creates a new content class by sending a POST request to the repository admin API using the provided JSON payload.
        TypeError: If the provided content_config is not an instance of ContentConfig.
        Exception: If an error occurs during the creation of the content class, it is logged and handled.
    """

    #--------------------------------------------------------------
    # Content Class definition
    class ContentClass:
        compress: bool = True
        encrypt: bool = False
        deleteExpiredAuto: bool = False
        type: int = 7
        description: str = ""
        details: str = "Note that %REPORTID% gets truncated to 8 characters.\nUse %REPORTID.10% to get the entire report ID.\nAlso, in general, avoid using relative paths."
        ocrProcessing: bool = True
        template: str = "/mnt/efs%PATHDELIM%%REPORTID%%PATHDELIM%%ARCHIVEDATE%%PATHDELIM%%ARCHIVETIME%%UNIQUE.2%.DAF"
        retentionType: str = "No retention"
        retentionBased: str = "Report version ID"
        enableMetadataIndexing: bool = True
        enableContentIndexing: bool = True
        redactionType: str = "No Redaction"
        securityTopic: str = ""
        characterType: str = "PC ANSI"
        daysForRetention: Optional[int] = None
        daysForRetentionWithInitialFixedPeriod: Optional[int] = None
        id: str
        name: str

        def __init__(self, id: str, name: str):
            self.id = id
            self.name = name
            self.compress = True
            self.encrypt = False
            self.deleteExpiredAuto = False
            self.type = 7
            self.description = ""
            self.details = "Note that %REPORTID% gets truncated to 8 characters.\nUse %REPORTID.10% to get the entire report ID.\nAlso, in general, avoid using relative paths."
            self.ocrProcessing = True
            self.template = "/mnt/efs%PATHDELIM%%REPORTID%%PATHDELIM%%ARCHIVEDATE%%PATHDELIM%%ARCHIVETIME%%UNIQUE.2%.DAF"
            self.retentionType = "No retention"
            self.retentionBased = "Report version ID"
            self.enableMetadataIndexing = True
            self.enableContentIndexing = True
            self.redactionType = "No Redaction"
            self.securityTopic = ""
            self.characterType = "PC ANSI"
            self.daysForRetention = None
            self.daysForRetentionWithInitialFixedPeriod = None

        def setEncrypt(self, encrypt: bool) -> None:
            self.encrypt = encrypt

        def to_dict(self):
            return {
                "compress": self.compress,
                "encrypt": self.encrypt,
                "deleteExpiredAuto": self.deleteExpiredAuto,
                "type": self.type,
                "description": self.description,
                "details": self.details,
                "ocrProcessing": self.ocrProcessing,
                "template": self.template,
                "retentionType": self.retentionType,
                "retentionBased": self.retentionBased,
                "enableMetadataIndexing": self.enableMetadataIndexing,
                "enableContentIndexing": self.enableContentIndexing,
                "redactionType": self.redactionType,
                "securityTopic": self.securityTopic,
                "characterType": self.characterType,
                "daysForRetention": self.daysForRetention,
                "daysForRetentionWithInitialFixedPeriod": self.daysForRetentionWithInitialFixedPeriod,
                "id": self.id,
                "name": self.name
            }    
        
    def __init__(self, content_config):

        if isinstance(content_config, ContentConfig):
            self.repo_admin_url = content_config.repo_admin_url
            self.logger = content_config.logger
            self.headers = deepcopy(content_config.headers)
        else:
            raise TypeError("ContentConfig class object expected")

    #--------------------------------------------------------------
    # Verify if Content Class definition exists
    # This method checks if a content class with the specified name exists by querying the admin reports API.
    # It returns True if the content class exists, otherwise returns False.
    # If an error occurs during the request or JSON parsing, it logs the error and returns False.
    def verify_content_class(self, cc_id) -> bool:
        """
        Verifies if a content class with the specified name exists by querying the admin reports API.
        Args:
            cc_id (str): The ID of the content class to verify.
        Returns:
            bool: True if an item with the given ID exists in the response, False otherwise.
        Raises:
            requests.HTTPError: If the HTTP request to the API fails.
            json.JSONDecodeError: If the response cannot be parsed as JSON.
        Logs:
            - Method name, request URL, and headers for debugging purposes.
        """
        try:
            local_headers = deepcopy(self.headers)
            local_headers['Accept'] = 'application/vnd.asg-mobius-admin-reports.v3+json,application/vnd.asg-mobius-admin-reports.v2+json,application/vnd.asg-mobius-admin-reports.v1+json'

            tm = str(int(time.time() * 1000))
            content_class_get_url = self.repo_admin_url + f"/reports?limit=5&&reportid={cc_id}&timestamp={tm}"

            self.logger.info("--------------------------------")
            self.logger.info("Method : verify_content_class")
            self.logger.debug(f"URL : {content_class_get_url}")
            self.logger.debug(f"Headers : {json.dumps(local_headers)}")
                         
            # Send the request
            response = requests.get(content_class_get_url, headers=local_headers, verify=False)
            
            # Check if the HTTP request was successful
            response.raise_for_status()
            
            # Parse JSON from response
            data = response.json()
          
            # Get items list, default to empty list if not found
            items = data.get("items", [])
            
            # Check each item for id == "AAA01"
            for item in items:
                if item.get("id") == cc_id:
                    return True
            return False
        
        except requests.HTTPError as e:
            self.logger.error(f"HTTP error occurred: {e}")
            return False
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return False       
    #--------------------------------------------------------------
    # Create Content Class definition
    def create_content_class(self, cc_id, cc_name): 
        """
        Creates a new content class by sending a POST request to the repository admin URL.
        Args:
            cc_id (str): The unique identifier for the content class.
            cc_name (str): The name of the content class.
        Returns:
            int: The HTTP status code returned by the POST request.
        Raises:
            Exception: Logs any exception that occurs during the process.
        Side Effects:
            - Logs method execution details, request headers, body, and response.
            - Sets encryption to True for the content class definition.
            - Modifies self.headers for content type and accept headers.
        """

        try:

            if self.verify_content_class(cc_id):
                self.logger.error(f"Content class with name '{cc_id}' already exists.")
                return 409

            # Create instance of ReportConfig with id and name
            content_class_definition = self.ContentClass(id=cc_id, name=cc_name)

            # Example: Set encrypt to True
            content_class_definition.setEncrypt(True)

            content_class_definition_url = self.repo_admin_url + "/reports?sourcereportidtoclone=AC001"
 
            self.headers['Content-Type'] = 'application/vnd.asg-mobius-admin-report.v1+json'
            self.headers['accept'] = 'application/vnd.asg-mobius-admin-report.v1+json'

            self.logger.info("--------------------------------")
            self.logger.info("Method : create_content_class")
            self.logger.debug(f"URL : {content_class_definition_url}")
            self.logger.debug(f"Headers : {json.dumps(self.headers)}")
            self.logger.debug(f"Payload : {json.dumps(content_class_definition.to_dict(), indent=2)}")  
                         
            # Send the request
            response = requests.post(content_class_definition_url, headers=self.headers, json=content_class_definition.to_dict(), verify=False)
            
            self.logger.info(f"Response Status Code: {response.status_code}")
            return response.status_code
         
        except Exception as e:
            self.logger.error(f"An error occurred: {e}")

    