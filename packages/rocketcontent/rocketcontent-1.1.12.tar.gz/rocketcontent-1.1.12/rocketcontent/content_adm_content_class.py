import json
import requests
import urllib3
import warnings
from copy import deepcopy

from .content_config import ContentConfig

from urllib.parse import quote

# Disable https warnings if the http certificate is not valid
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

class ContentAdmContentClass:
    
    def __init__(self, content_config):

        if isinstance(content_config, ContentConfig):
            self.repo_admin_url = content_config.repo_admin_url
            self.logger = content_config.logger
            self.headers = deepcopy(content_config.headers)
        else:
            raise TypeError("ContentConfig class object expected")
        
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
        try:

            content_class_definition_url = self.repo_admin_url + "/reports"
    
            self.headers['Content-Type'] = 'application/vnd.asg-mobius-admin-report.v1+json'
            self.headers['Accept'] = 'application/vnd.asg-mobius-admin-reports.v3+json'

            self.logger.info("--------------------------------")
            self.logger.info("Method : create_content_class")
            self.logger.debug(f"URL : {content_class_definition_url}")
            self.logger.debug(f"Headers : {json.dumps(self.headers)}")
            self.logger.debug(f"Body : {json.dumps(content_class_json)}")
                
            # Send the request
            response = requests.post(content_class_definition_url, headers=self.headers, data=content_class_json, verify=False)
            
            self.logger.debug(response.text) 
            self.logger.info(f"Response Status Code: {response.status_code}")
            return response.status_code
         
        except Exception as e:
            self.logger.error(f"An error occurred: {e}")

    