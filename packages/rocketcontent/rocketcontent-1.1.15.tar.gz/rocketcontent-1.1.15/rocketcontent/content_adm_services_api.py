import urllib3
import warnings

from .content_config import ContentConfig
from .content_adm_archive_policy import ContentAdmArchivePolicy
from .content_adm_content_class import ContentAdmContentClass
from .content_adm_index_group import ContentAdmIndexGroup

# Disable https warnings if the http certificate is not valid
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

class ContentAdmServicesApi:
    """
    ContentAdnServicesApi is the main class for interacting with Mobius ADMIN REST content_obj.

    Attributes:
        config: is a ContentConfig object with information about connection, and logging ,etc.
    """
    def __init__(self, yaml_file):
        """
        Initializes the ContentAdmServicesApi class from YAML file.
        
        Args:
            yaml_file: [Mandatory] Path to the YAML configuration 
        """
        self.config = ContentConfig(yaml_file)
 
    #--------------------------------------------------------------
    # Import Archiving Policy
    def import_archiving_policy(self, archiving_policy_path, archiving_policy_name):
        """
        Import an archiving policy by reading a JSON file and sending it via POST request.
        
        Args:
            archiving_policy_path (str): Path to the JSON file containing the archiving policy.
            archiving_policy_name (str): Name of the archiving policy.
        
        Returns:
            int: HTTP status code of the response, or None if an error occurs.
        """
        repo = ContentAdmArchivePolicy(self.config)

        return repo.import_archiving_policy(archiving_policy_path, archiving_policy_name)
    
    #--------------------------------------------------------------
    # Create Content Class definition
    def create_content_class(self, content_class_json): 
        """
        Creates a new content class by sending a POST request to the repository admin API.
        Args:
            content_class_json (dict): The JSON payload defining the content class to be created.
        Returns:
            int: The HTTP status code returned by the API after attempting to create the content class.
        Raises:
            Exception: Logs and handles any exceptions that occur during the request.
        """
        repo = ContentAdmContentClass(self.config)

        return repo.create_content_class(content_class_json)
    
    #--------------------------------------------------------------
    # Create Index Group Definition
    def create_index_group(self, index_group_json):
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
        repo = ContentAdmIndexGroup(self.config)
    
        return repo.create_index_group(index_group_json)
    