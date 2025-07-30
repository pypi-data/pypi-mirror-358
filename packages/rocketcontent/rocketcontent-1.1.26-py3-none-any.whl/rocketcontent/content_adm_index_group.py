import json
import requests
import urllib3
import warnings
from typing import List, Dict, Any, Optional
from copy import deepcopy
from .content_config import ContentConfig
from urllib.parse import quote
import time

# Disable https warnings if the http certificate is not valid
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)


class Topic:
    id: str
    name: str
    details: str
    topicVersionDisplay: str
    allowAccess: bool
    dataType: str
    maxLength: str
    category: str
    enableIndex: bool

    def __init__(self, id: str, name: str, details: str, dataType: str = "Character", maxLength: str = "30"):

        if dataType not in ["Character", "Date", "Number"]:
            raise ValueError("dataType must be one of 'Character', 'Date', or 'Number'.")
        
        if maxLength not in ["30", "255"]:
            raise ValueError("maxLength must be one of '30', or '255'.")

        self.id = id
        self.name = name
        self.details = details
        self.dataType = dataType
        self.maxLength = maxLength
        self.topicVersionDisplay = "All"
        self.allowAccess = True
        self.category = "Document metadata"
        self.enableIndex = True

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Topic':
        """Create a Topic instance from a dictionary."""
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            details=data.get("details", ""),
            dataType=data.get("dataType", "Character"),
            maxLength=data.get("maxLength", "30")
        )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "details": self.details,
            "topicVersionDisplay": self.topicVersionDisplay,
            "allowAccess": self.allowAccess,
            "dataType": self.dataType,
            "maxLength": self.maxLength,
            "category": self.category,
            "enableIndex": self.enableIndex
        }


class IndexGroup:
    id: str
    name: str
    scope: str
    topics: List[Topic]

    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name
        self.scope = "Line"
        self.topics = []

    def addTopic(self, topic: Topic) -> None:
        """Add a Topic object to the topics list."""
        self.topics.append(topic)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IndexGroup':
        """Create an IndexGroup instance from a dictionary."""
        index_group = cls(
            id=data.get("id", ""),
            name=data.get("name", "")
        )
        for topic_data in data.get("topics", []):
            index_group.addTopic(Topic.from_dict(topic_data))
        return index_group

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "scope": self.scope,
            "topics": [topic.to_dict() for topic in self.topics]
        }
    
class ContentAdmIndexGroup:
    def __init__(self, content_config):

        if isinstance(content_config, ContentConfig):
            self.repo_admin_url = content_config.repo_admin_url
            self.logger = content_config.logger
            self.headers = deepcopy(content_config.headers)
        else:
            raise TypeError("ContentConfig class object expected")
            
 
    #--------------------------------------------------------------
    # Verify if Index Group definition exists
    # This method checks if a index group with the specified id exists.
    # It returns True if the index group exists, otherwise returns False.
    # If an error occurs during the request or JSON parsing, it logs the error and returns False.
    def verify_index_group(self, ig_id) -> bool:
        """
        Verifies if a index group the specified name exists by querying the admin reports API.
        Args:
            ig_id (str): The ID of the index group to verify.
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
            local_headers['Accept'] = 'application/vnd.asg-mobius-admin-topic-groups.v1+json'

            tm = str(int(time.time() * 1000))
            index_group_get_url = self.repo_admin_url + f"/topicgroups?limit=5&&groupid={ig_id}&timestamp={tm}"

            self.logger.info("--------------------------------")
            self.logger.info("Method : verify_index_group")
            self.logger.debug(f"URL : {index_group_get_url}")
            self.logger.debug(f"Headers : {json.dumps(local_headers)}")
                         
            # Send the request
            response = requests.get(index_group_get_url, headers=local_headers, verify=False)
            
            # Check if the HTTP request was successful
            response.raise_for_status()
            
            # Parse JSON from response
            data = response.json()
          
            # Get items list, default to empty list if not found
            items = data.get("items", [])
            
            # Check each item for id == "AAA01"
            for item in items:
                if item.get("id") == ig_id:
                    return True
            return False
        
        except requests.HTTPError as e:
            self.logger.error(f"HTTP error occurred: {e}")
            return False
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return False       
        
    #--------------------------------------------------------------
    # Create Index Group Definition
    def create_index_group(self, index_group: IndexGroup) -> int:
        """
        Creates a new index group by sending a POST request to the repository admin API.
        Args:
            index_group_json (dict): The JSON payload containing the index group definition.
        Returns:
            int: The HTTP status code returned by the API.
        Logs:
            - Method entry and exit points.
            - Request URL, headers, and body.
            - Response text.
            - Errors encountered during the process.
        Raises:
            Logs any exceptions that occur during the request.
        """
        try:

            if self.verify_index_group(index_group.id):
                self.logger.error(f"Index Group with name '{index_group.id}' already exists.")
                return 409
               
            index_group_definition_url= self.repo_admin_url + "/topicgroups"
    
            self.headers['Content-Type'] = 'application/vnd.asg-mobius-admin-topic-group.v1+json'
            self.headers['Accept'] = 'application/vnd.asg-mobius-admin-topic-group.v1+json'

            self.logger.info("--------------------------------")
            self.logger.info("Method : create_index_group")
            self.logger.debug(f"URL : {index_group_definition_url}")
            self.logger.debug(f"Headers : {json.dumps(self.headers)}")
            self.logger.debug(f"Payload : {json.dumps(index_group.to_dict(),indent=2)}")
               
            # Send the request
            response = requests.post(index_group_definition_url, headers=self.headers, json=index_group.to_dict(), verify=False)
            
            self.logger.info(f"Response Status Code: {response.status_code}")
            return response.status_code
        
        except Exception as e:
            self.logger.error(f"An error occurred: {e}")

