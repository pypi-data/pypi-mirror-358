"""
Victoria Dates API client
"""

import os
import yaml
import requests
from typing import Optional
from .models import ImportantDate, ImportantDatesResponse


class VictoriaDatesClient:
    """Client for the Victoria, Australia important dates API"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        """
        Initialize the Victoria Dates client
        
        Args:
            api_key: API key for authentication
            api_secret: API secret for authentication  
            base_url: Base URL for the API
        """
        # Load configuration
        self._load_config()
        
        # Override with provided parameters
        self.api_key = api_key or self.api_key
        self.api_secret = api_secret or self.api_secret
        self.base_url = base_url or self.base_url
        
        if not self.base_url:
            raise ValueError("Base URL is required. Set it via parameter, environment variable, or config file.")
    
    def _load_config(self):
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            # dotenv not available, continue without it
            pass
        """Load configuration from environment variables and config.yaml"""
        # Default values
        self.api_key = None
        self.api_secret = None
        self.base_url = None
        
        # Try to load from config.yaml
        try:
            with open("config.yaml", "r") as f:
                config = yaml.safe_load(f)
                
            # Get API key
            api_key_var = config.get("apiKeyVariableName")
            if api_key_var:
                self.api_key = os.getenv(api_key_var) or os.getenv(api_key_var.upper())
            
            # Get API secret
            api_secret_var = config.get("apiSecretVariableName")
            if api_secret_var:
                self.api_secret = os.getenv(api_secret_var) or os.getenv(api_secret_var.upper())
            
            # Get base URL
            self.base_url = os.getenv("BASE_URL") or config.get("baseUrl")
            
        except FileNotFoundError:
            # If config.yaml doesn't exist, try environment variables directly
            self.api_key = os.getenv("DEVELOPER_VIC_GOV_AU_KEY")
            self.api_secret = os.getenv("DEVELOPER_VIC_GOV_AU_SECRET")
            self.base_url = os.getenv("BASE_URL")
    
    def fetch_dates(
        self, 
        type: str, 
        from_date: str, 
        to_date: str, 
        format: str = "json"
    ) -> Optional[ImportantDatesResponse]:
        """
        Fetch important dates from the API
        
        Args:
            type: Type of dates to fetch (PUBLIC_HOLIDAY, SCHOOL_TERM, etc.)
            from_date: Start date in YYYY-MM-DD format
            to_date: End date in YYYY-MM-DD format
            format: Response format (default: "json")
            
        Returns:
            ImportantDatesResponse object or None if request fails
        """
        api_endpoint = f"{self.base_url}/dates?type={type}&from_date={from_date}&to_date={to_date}&format={format}"
        
        headers = {
            "Accept": "application/json",
            "User-Agent": "victoria-dates-client/1.0",
        }
        
        if self.api_key:
            headers["apikey"] = self.api_key
        
        response = requests.get(api_endpoint, headers=headers)
        
        if response.status_code == 200:
            try:
                data = response.json()
                return ImportantDatesResponse.model_validate(data)
            except Exception as e:
                print(f"Error parsing response: {e}")
        else:
            print(f"Failed to fetch data: {response.status_code}")
            print(response.text)
        
        return None
    
    def fetch_date_by_id(self, date_id: str) -> Optional[ImportantDate]:
        """
        Fetch a specific date by its ID
        
        Args:
            date_id: The ID of the date to fetch
            
        Returns:
            ImportantDate object or None if request fails
        """
        api_endpoint = f"{self.base_url}/{date_id}"
        
        headers = {
            "Accept": "application/json",
            "User-Agent": "victoria-dates-client/1.0",
        }
        
        if self.api_key:
            headers["apikey"] = self.api_key
        
        response = requests.get(api_endpoint, headers=headers)
        
        if response.status_code == 200:
            try:
                data = response.json()
                return ImportantDate.model_validate(data)
            except Exception as e:
                print(f"Error parsing response: {e}")
        else:
            print(f"Failed to fetch data: {response.status_code}")
            print(response.text)
        
        return None 