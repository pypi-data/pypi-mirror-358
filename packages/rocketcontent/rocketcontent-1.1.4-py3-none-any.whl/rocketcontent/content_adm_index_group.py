import json
import requests
import urllib3
import warnings

from .content_config import ContentConfig

from urllib.parse import quote

# Disable https warnings if the http certificate is not valid
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

class ContentAdmIndexGroup:
    def __init__(self, content_config):

        if isinstance(content_config, ContentConfig):
            self.repo_url = content_config.repo_url
            self.repo_id = content_config.repo_id
            self.logger = content_config.logger
            self.repo_admin_url = content_config.base_url + content_config.repo_id_enc
            self.encoded_repo_credentials = content_config.encoded_repo_credentials
            self.authorization_repo = content_config.authorization_repo
        else:
            raise TypeError("ContentConfig class object expected")
            
 
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
        try:
            index_group_definition_url= self.repo_admin_url + "/topicgroups"
    
            headers = {
                'Accept': 'application/vnd.asg-mobius-admin-topic-group.v1+json',
                'Content-Type': 'application/vnd.asg-mobius-admin-topic-group.v1+json',
                'Authorization': f'Basic {self.encoded_credentials}'
                }

            self.logger.info("--------------------------------")
            self.logger.info("Method : create_index_group")
            self.logger.debug(f"URL : {index_group_definition_url}")
            self.logger.debug(f"Headers : {json.dumps(headers)}")
            self.logger.debug(f"Body : {json.dumps(index_group_json)}")
                
            # Send the request
            response = requests.post(index_group_definition_url, headers=headers, data=index_group_json, verify=False)
            
            self.logger.debug(response.text)
        
            return response.status_code
        
        except Exception as e:
            self.logger.error(f"An error occurred: {e}")