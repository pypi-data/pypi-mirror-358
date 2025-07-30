"""
Acquisition-related commands for the Binalyze AIR SDK.
Fixed to match API documentation exactly.
"""

from typing import List, Dict, Any

from ..base import Command
from ..models.acquisitions import (
    AcquisitionTaskRequest, ImageAcquisitionTaskRequest, CreateAcquisitionProfileRequest,
    CreateAcquisitionRequest, CreateImageAcquisitionRequest
)
from ..models.assets import AssetFilter
from ..http_client import HTTPClient


class AssignAcquisitionTaskCommand(Command[List[Dict[str, Any]]]):
    """Command to assign acquisition task - FIXED to match API documentation exactly."""
    
    def __init__(self, http_client: HTTPClient, request: AcquisitionTaskRequest):
        self.http_client = http_client
        self.request = request
    
    def execute(self) -> List[Dict[str, Any]]:
        """Execute the acquisition task assignment with correct payload structure."""
        # FIXED: Use proper API payload structure as per documentation
        payload = {
            "caseId": self.request.case_id,
            "acquisitionProfileId": self.request.acquisition_profile_id,
            "droneConfig": {
                "autoPilot": self.request.drone_config.auto_pilot if self.request.drone_config else False,
                "enabled": self.request.drone_config.enabled if self.request.drone_config else False,
                "analyzers": self.request.drone_config.analyzers if self.request.drone_config else ["bha", "wsa", "aa", "ara"],
                "keywords": self.request.drone_config.keywords if self.request.drone_config else []
            },
            "taskConfig": {
                "choice": self.request.task_config.choice if self.request.task_config else "use-custom-options",
                "saveTo": {
                    "windows": {
                        "location": "local",
                        "useMostFreeVolume": True,
                        "repositoryId": None,
                        "path": "Binalyze\\AIR\\",
                        "volume": "C:",
                        "tmp": "Binalyze\\AIR\\tmp",
                        "directCollection": False
                    },
                    "linux": {
                        "location": "local",
                        "useMostFreeVolume": True,
                        "repositoryId": None,
                        "path": "opt/binalyze/air",
                        "tmp": "opt/binalyze/air/tmp",
                        "directCollection": False
                    },
                    "macos": {
                        "location": "local",
                        "useMostFreeVolume": False,
                        "repositoryId": None,
                        "path": "opt/binalyze/air",
                        "volume": "/",
                        "tmp": "opt/binalyze/air/tmp",
                        "directCollection": False
                    },
                    "aix": {
                        "location": "local",
                        "useMostFreeVolume": True,
                        "path": "opt/binalyze/air",
                        "volume": "/",
                        "tmp": "opt/binalyze/air/tmp",
                        "directCollection": False
                    }
                },
                "cpu": self.request.task_config.cpu if self.request.task_config else {"limit": 80},
                "compression": self.request.task_config.compression if self.request.task_config else {
                    "enabled": True,
                    "encryption": {
                        "enabled": False,
                        "password": ""
                    }
                }
            },
            "filter": {
                "searchTerm": self.request.filter.search_term or "",
                "name": self.request.filter.name or "",
                "ipAddress": self.request.filter.ip_address or "",
                "groupId": self.request.filter.group_id or "",
                "groupFullPath": self.request.filter.group_full_path or "",
                "managedStatus": self.request.filter.managed_status or [],
                "isolationStatus": self.request.filter.isolation_status or [],
                "platform": self.request.filter.platform or [],
                "issue": self.request.filter.issue or "",
                "onlineStatus": self.request.filter.online_status or [],
                "tags": self.request.filter.tags or [],
                "version": self.request.filter.version or "",
                "policy": self.request.filter.policy or "",
                "includedEndpointIds": self.request.filter.included_endpoint_ids or [],
                "excludedEndpointIds": self.request.filter.excluded_endpoint_ids or [],
                "organizationIds": self.request.filter.organization_ids or [0]
            },
            "schedulerConfig": {
                "when": "now"
            }
        }
        
        # FIXED: Correct endpoint URL
        response = self.http_client.post("acquisitions/acquire", json_data=payload)
        
        return response.get("result", [])


class CreateAcquisitionCommand(Command[Dict[str, Any]]):
    """Command to create acquisition task using simplified request - FIXED to match API."""
    
    def __init__(self, http_client: HTTPClient, request: CreateAcquisitionRequest):
        self.http_client = http_client
        self.request = request
    
    def execute(self) -> Dict[str, Any]:
        """Execute the acquisition task assignment with correct structure."""
        # FIXED: Use proper filter structure instead of direct filter object
        payload = {
            "caseId": getattr(self.request, 'case_id', None),
            "acquisitionProfileId": self.request.profileId,
            "droneConfig": {
                "autoPilot": False,
                "enabled": False,
                "analyzers": ["bha", "wsa", "aa", "ara"],
                "keywords": []
            },
            "taskConfig": {
                "choice": "use-custom-options",
                "saveTo": {
                    "windows": {
                        "location": "local",
                        "useMostFreeVolume": True,
                        "repositoryId": None,
                        "path": "Binalyze\\AIR\\",
                        "volume": "C:",
                        "tmp": "Binalyze\\AIR\\tmp",
                        "directCollection": False
                    },
                    "linux": {
                        "location": "local",
                        "useMostFreeVolume": True,
                        "repositoryId": None,
                        "path": "opt/binalyze/air",
                        "tmp": "opt/binalyze/air/tmp",
                        "directCollection": False
                    },
                    "macos": {
                        "location": "local",
                        "useMostFreeVolume": False,
                        "repositoryId": None,
                        "path": "opt/binalyze/air",
                        "volume": "/",
                        "tmp": "opt/binalyze/air/tmp",
                        "directCollection": False
                    },
                    "aix": {
                        "location": "local",
                        "useMostFreeVolume": True,
                        "path": "opt/binalyze/air",
                        "volume": "/",
                        "tmp": "opt/binalyze/air/tmp",
                        "directCollection": False
                    }
                },
                "cpu": {
                    "limit": 80
                },
                "compression": {
                    "enabled": True,
                    "encryption": {
                        "enabled": False,
                        "password": ""
                    }
                }
            },
            "filter": self.request.filter.to_filter_dict() if isinstance(self.request.filter, AssetFilter) else self.request.filter,
            "schedulerConfig": {
                "when": "now"
            }
        }
        
        if hasattr(self.request, 'name') and self.request.name:
            payload["taskName"] = self.request.name
        
        return self.http_client.post("acquisitions/acquire", json_data=payload)


class AssignImageAcquisitionTaskCommand(Command[List[Dict[str, Any]]]):
    """Command to assign image acquisition task by filter."""
    
    def __init__(self, http_client: HTTPClient, request: ImageAcquisitionTaskRequest):
        self.http_client = http_client
        self.request = request
    
    def execute(self) -> List[Dict[str, Any]]:
        """Execute the image acquisition task assignment."""
        
        # Build payload with proper API field names (camelCase)
        payload = {
            "caseId": self.request.case_id,
            "taskConfig": {
                "choice": self.request.task_config.choice,
                "saveTo": {},
                "cpu": self.request.task_config.cpu,
                "bandwidth": getattr(self.request.task_config, 'bandwidth', {"limit": 100000}),
                "compression": self.request.task_config.compression
            },
            "diskImageOptions": {
                "startOffset": self.request.disk_image_options.startOffset,
                "chunkSize": self.request.disk_image_options.chunkSize,
                "chunkCount": self.request.disk_image_options.chunkCount,
                "imageType": getattr(self.request.disk_image_options, 'imageType', 'dd'),
                "singleFile": getattr(self.request.disk_image_options, 'singleFile', False),
                "endpoints": [
                    {
                        "endpointId": ep.endpointId,
                        "volumes": ep.volumes
                    }
                    for ep in self.request.disk_image_options.endpoints
                ]
            },
            "filter": {
                "searchTerm": getattr(self.request.filter, 'search_term', '') or '',
                "name": getattr(self.request.filter, 'name', '') or '',
                "ipAddress": getattr(self.request.filter, 'ip_address', '') or '',
                "groupId": getattr(self.request.filter, 'group_id', '') or '',
                "groupFullPath": getattr(self.request.filter, 'group_full_path', '') or '',
                "managedStatus": getattr(self.request.filter, 'managed_status', []),
                "isolationStatus": getattr(self.request.filter, 'isolation_status', []),
                "platform": getattr(self.request.filter, 'platform', []),
                "issue": getattr(self.request.filter, 'issue', '') or '',
                "onlineStatus": getattr(self.request.filter, 'online_status', []),
                "tags": getattr(self.request.filter, 'tags', []),
                "version": getattr(self.request.filter, 'version', '') or '',
                "policy": getattr(self.request.filter, 'policy', '') or '',
                "includedEndpointIds": getattr(self.request.filter, 'included_endpoint_ids', []),
                "excludedEndpointIds": getattr(self.request.filter, 'excluded_endpoint_ids', []),
                "organizationIds": getattr(self.request.filter, 'organization_ids', [0])
            }
        }
        
        # Build saveTo configuration with proper API field names
        for platform, config in self.request.task_config.save_to.items():
            if hasattr(config, 'location'):
                platform_config = {
                    "location": config.location,
                    "useMostFreeVolume": config.use_most_free_volume,  # FIXED: camelCase
                    "path": config.path,
                    "tmp": config.tmp,
                    "directCollection": config.direct_collection  # FIXED: camelCase
                }
                
                # Add optional fields with proper names
                if hasattr(config, 'repository_id') and config.repository_id:
                    platform_config["repositoryId"] = config.repository_id  # FIXED: camelCase
                if hasattr(config, 'volume') and config.volume:
                    platform_config["volume"] = config.volume
                    
                payload["taskConfig"]["saveTo"][platform] = platform_config
            else:
                # Handle dict-based config
                payload["taskConfig"]["saveTo"][platform] = config
        
        # Add scheduler config if present (matching API spec)
        if hasattr(self.request, 'scheduler_config') and self.request.scheduler_config:
            payload["schedulerConfig"] = {
                "when": getattr(self.request.scheduler_config, 'when', 'now')
            }
            # Add other scheduler fields if present
            for field in ['timezone_type', 'timezone', 'start_date', 'recurrence', 'repeat_every', 'repeat_on_week', 'repeat_on_month', 'end_repeat_type', 'end_date', 'limit']:
                if hasattr(self.request.scheduler_config, field) and getattr(self.request.scheduler_config, field) is not None:
                    # Convert snake_case to camelCase for API
                    api_field = field.replace('_', '')
                    if field == 'timezone_type':
                        api_field = 'timezoneType'
                    elif field == 'start_date':
                        api_field = 'startDate'
                    elif field == 'repeat_every':
                        api_field = 'repeatEvery'
                    elif field == 'repeat_on_week':
                        api_field = 'repeatOnWeek'
                    elif field == 'repeat_on_month':
                        api_field = 'repeatOnMonth'
                    elif field == 'end_repeat_type':
                        api_field = 'endRepeatType'
                    elif field == 'end_date':
                        api_field = 'endDate'
                    payload["schedulerConfig"][api_field] = getattr(self.request.scheduler_config, field)
        else:
            # Default scheduler config as per API spec
            payload["schedulerConfig"] = {"when": "now"}
        
        response = self.http_client.post("acquisitions/acquire/image", json_data=payload)
        
        # Extract result list from response
        if isinstance(response, dict) and "result" in response:
            return response["result"] if isinstance(response["result"], list) else [response["result"]]
        return []


class CreateImageAcquisitionCommand(Command[Dict[str, Any]]):
    """Command to create image acquisition task - FIXED with required fields."""
    
    def __init__(self, http_client: HTTPClient, request: CreateImageAcquisitionRequest):
        self.http_client = http_client
        self.request = request
    
    def execute(self) -> Dict[str, Any]:
        """Execute the image acquisition task creation with proper API structure."""
        
        # Build complete payload structure matching API specification
        payload = {
            "caseId": getattr(self.request, 'case_id', None)
        }
        
        # Use task_config from request if provided, otherwise use defaults
        if hasattr(self.request, 'task_config') and self.request.task_config:
            if isinstance(self.request.task_config, dict):
                payload["taskConfig"] = self.request.task_config
            else:
                payload["taskConfig"] = self.request.task_config.model_dump()
        else:
            # Default task config
            payload["taskConfig"] = {
                "choice": "use-custom-options",
                "saveTo": {
                    "windows": {
                        "location": "repository",
                        "path": "Binalyze\\AIR",
                        "useMostFreeVolume": True,
                        "repositoryId": "DEFAULT_REPOSITORY_ID",
                        "tmp": "Binalyze\\AIR\\tmp",
                        "directCollection": False
                    },
                    "linux": {
                        "location": "repository", 
                        "path": "opt/binalyze/air",
                        "useMostFreeVolume": False,
                        "repositoryId": "DEFAULT_REPOSITORY_ID",
                        "tmp": "opt/binalyze/air/tmp",
                        "directCollection": False
                    },
                    "macos": {
                        "location": "repository",
                        "path": "opt/binalyze/air", 
                        "useMostFreeVolume": False,
                        "repositoryId": "DEFAULT_REPOSITORY_ID",
                        "tmp": "opt/binalyze/air/tmp",
                        "directCollection": False
                    }
                },
                "cpu": {"limit": 50},
                "bandwidth": {"limit": 100000},
                "compression": {
                    "enabled": True,
                    "encryption": {
                        "enabled": False,
                        "password": ""
                    }
                }
            }
        
        # Use disk_image_options from request if provided, otherwise use defaults
        if hasattr(self.request, 'disk_image_options') and self.request.disk_image_options:
            if isinstance(self.request.disk_image_options, dict):
                payload["diskImageOptions"] = self.request.disk_image_options
            else:
                payload["diskImageOptions"] = self.request.disk_image_options.model_dump()
        else:
            # Default disk image options
            payload["diskImageOptions"] = {
                "chunkSize": 1048576,
                "chunkCount": 0,
                "startOffset": 0,
                "imageType": "dd",
                "singleFile": False,
                "endpoints": [{
                    "endpointId": "SDK_TEST_NONEXISTENT_ENDPOINT",
                    "volumes": ["/dev/test"]
                }]
            }
        
        # Use scheduler_config from request if provided, otherwise use default
        if hasattr(self.request, 'scheduler_config') and self.request.scheduler_config:
            if isinstance(self.request.scheduler_config, dict):
                payload["schedulerConfig"] = self.request.scheduler_config
            else:
                payload["schedulerConfig"] = self.request.scheduler_config.model_dump()
        else:
            payload["schedulerConfig"] = {"when": "now"}
        
        # Use the filter from request
        if hasattr(self.request, 'filter') and self.request.filter:
            if isinstance(self.request.filter, dict):
                payload["filter"] = self.request.filter
            else:
                payload["filter"] = self.request.filter.model_dump()
        
        # Add task name if provided
        if hasattr(self.request, 'name') and self.request.name:
            payload["taskName"] = self.request.name
        
        return self.http_client.post("acquisitions/acquire/image", json_data=payload)


class CreateAcquisitionProfileCommand(Command[Dict[str, Any]]):
    """Command to create acquisition profile - FIXED field conversion."""
    
    def __init__(self, http_client: HTTPClient, request: CreateAcquisitionProfileRequest):
        self.http_client = http_client
        self.request = request
    
    def execute(self) -> Dict[str, Any]:
        """Execute the create acquisition profile command."""
        # Build the payload
        payload = {
            "name": self.request.name,
            "organizationIds": self.request.organizationIds if self.request.organizationIds else []
        }
        
        # Convert platform configuration to API format - FIXED conversion logic
        def convert_platform_to_api(platform_data, platform_name=""):
            if not platform_data:
                return None
            
            # FIXED: Use model_dump() for reliable field access
            api_data = platform_data.model_dump()
            
            # Remove networkCapture from AIX platform as per API spec
            if platform_name.lower() == "aix" and "networkCapture" in api_data:
                del api_data["networkCapture"]
            
            return api_data
        
        # Add platform configurations with proper platform names
        if self.request.windows:
            payload["windows"] = convert_platform_to_api(self.request.windows, "windows")
        if self.request.linux:
            payload["linux"] = convert_platform_to_api(self.request.linux, "linux")
        if self.request.macos:
            payload["macos"] = convert_platform_to_api(self.request.macos, "macos")
        if self.request.aix:
            payload["aix"] = convert_platform_to_api(self.request.aix, "aix")
        
        # Handle eDiscovery field if present
        if hasattr(self.request, 'eDiscovery') and self.request.eDiscovery:
            # Convert EDiscoveryConfig to the expected dict format for API
            if hasattr(self.request.eDiscovery, 'patterns'):
                payload["eDiscovery"] = {
                    "patterns": [
                        pattern.model_dump()
                        for pattern in self.request.eDiscovery.patterns
                    ]
                }
            elif hasattr(self.request.eDiscovery, 'model_dump'):
                # Handle as pydantic model
                payload["eDiscovery"] = self.request.eDiscovery.model_dump()
            elif isinstance(self.request.eDiscovery, dict):
                # Handle as dictionary
                payload["eDiscovery"] = self.request.eDiscovery
        
        return self.http_client.post("acquisitions/profiles", json_data=payload)


class UpdateAcquisitionProfileCommand(Command[Dict[str, Any]]):
    """Command to update acquisition profile by ID - FIXED field conversion."""
    
    def __init__(self, http_client: HTTPClient, profile_id: str, request: CreateAcquisitionProfileRequest):
        self.http_client = http_client
        self.profile_id = profile_id
        self.request = request
    
    def execute(self) -> Dict[str, Any]:
        """Execute the update acquisition profile command."""
        # Build the payload (same structure as create)
        payload = {
            "name": self.request.name,
            "organizationIds": self.request.organizationIds if self.request.organizationIds else []
        }
        
        # Convert platform configuration to API format - FIXED conversion logic
        def convert_platform_to_api(platform_data, platform_name=""):
            if not platform_data:
                return None
            
            # FIXED: Use model_dump() for reliable field access
            api_data = platform_data.model_dump()
            
            # Remove networkCapture from AIX platform as per API spec
            if platform_name.lower() == "aix" and "networkCapture" in api_data:
                del api_data["networkCapture"]
            
            return api_data
        
        # Add platform configurations with proper platform names
        if self.request.windows:
            payload["windows"] = convert_platform_to_api(self.request.windows, "windows")
        if self.request.linux:
            payload["linux"] = convert_platform_to_api(self.request.linux, "linux")
        if self.request.macos:
            payload["macos"] = convert_platform_to_api(self.request.macos, "macos")
        if self.request.aix:
            payload["aix"] = convert_platform_to_api(self.request.aix, "aix")
        
        # Handle eDiscovery field if present
        if hasattr(self.request, 'eDiscovery') and self.request.eDiscovery:
            # Convert EDiscoveryConfig to the expected dict format for API
            if hasattr(self.request.eDiscovery, 'patterns'):
                payload["eDiscovery"] = {
                    "patterns": [
                        pattern.model_dump()
                        for pattern in self.request.eDiscovery.patterns
                    ]
                }
            elif hasattr(self.request.eDiscovery, 'model_dump'):
                # Handle as pydantic model
                payload["eDiscovery"] = self.request.eDiscovery.model_dump()
            elif isinstance(self.request.eDiscovery, dict):
                # Handle as dictionary
                payload["eDiscovery"] = self.request.eDiscovery
        
        return self.http_client.put(f"acquisitions/profiles/{self.profile_id}", json_data=payload)


class DeleteAcquisitionProfileCommand(Command[Dict[str, Any]]):
    """Command to delete acquisition profile by ID."""
    
    def __init__(self, http_client: HTTPClient, profile_id: str):
        self.http_client = http_client
        self.profile_id = profile_id
    
    def execute(self) -> Dict[str, Any]:
        """Execute the delete acquisition profile command."""
        return self.http_client.delete(f"acquisitions/profiles/{self.profile_id}")


class CreateOffNetworkAcquisitionCommand(Command[Dict[str, Any]]):
    """Command to create evidence acquisition off-network task."""
    
    def __init__(self, http_client: HTTPClient, request: CreateAcquisitionRequest):
        self.http_client = http_client
        self.request = request
    
    def execute(self) -> Dict[str, Any]:
        """Execute the off-network acquisition task creation."""
        # Build payload structure matching the API specification
        payload = {
            "caseId": getattr(self.request, 'case_id', None),
            "acquisitionProfileId": self.request.profileId,
            "droneConfig": {
                "autoPilot": False,
                "enabled": False,
                "analyzers": ["bha", "wsa", "aa", "ara"],
                "keywords": []
            },
            "eventLogRecordsConfig": {
                "startDate": None,
                "endDate": None,
                "maxEventCount": 1000
            },
            "taskConfig": {
                "choice": "use-custom-options",
                "saveTo": {
                    "windows": {
                        "location": "local",
                        "useMostFreeVolume": True,
                        "repositoryId": None,
                        "path": "Binalyze\\AIR\\",
                        "volume": "C:",
                        "tmp": "Binalyze\\AIR\\tmp",
                        "directCollection": False
                    },
                    "linux": {
                        "location": "local",
                        "useMostFreeVolume": True,
                        "repositoryId": None,
                        "path": "opt/binalyze/air",
                        "tmp": "opt/binalyze/air/tmp",
                        "directCollection": False
                    },
                    "macos": {
                        "location": "local",
                        "useMostFreeVolume": False,
                        "repositoryId": None,
                        "path": "opt/binalyze/air",
                        "volume": "/",
                        "tmp": "opt/binalyze/air/tmp",
                        "directCollection": False
                    },
                    "aix": {
                        "location": "local",
                        "useMostFreeVolume": True,
                        "path": "opt/binalyze/air",
                        "volume": "/",
                        "tmp": "opt/binalyze/air/tmp",
                        "directCollection": False
                    }
                },
                "cpu": {
                    "limit": 80
                },
                "compression": {
                    "enabled": True,
                    "encryption": {
                        "enabled": False,
                        "password": ""
                    }
                }
            },
            "filter": self.request.filter.to_filter_dict() if isinstance(self.request.filter, AssetFilter) else self.request.filter,
            "schedulerConfig": {
                "when": "now"
            }
        }
        
        if hasattr(self.request, 'name') and self.request.name:
            payload["taskName"] = self.request.name
        
        return self.http_client.post("acquisitions/acquire/off-network", json_data=payload)


class UpdateScheduledEvidenceAcquisitionCommand(Command[Dict[str, Any]]):
    """Command to update scheduled evidence acquisition."""
    
    def __init__(self, http_client: HTTPClient, task_id: str, request: Dict[str, Any]):
        self.http_client = http_client
        self.task_id = task_id
        self.request = request
    
    def execute(self) -> Dict[str, Any]:
        """Execute the update scheduled evidence acquisition command."""
        return self.http_client.put(f"acquisitions/schedule/evidence-acquisition/{self.task_id}", json_data=self.request)


class UpdateScheduledImageAcquisitionCommand(Command[Dict[str, Any]]):
    """Command to update scheduled image acquisition."""
    
    def __init__(self, http_client: HTTPClient, task_id: str, request: Dict[str, Any]):
        self.http_client = http_client
        self.task_id = task_id
        self.request = request
    
    def execute(self) -> Dict[str, Any]:
        """Execute the update scheduled image acquisition command."""
        return self.http_client.put(f"acquisitions/schedule/image-acquisition/{self.task_id}", json_data=self.request)


class ValidateOsqueryCommand(Command[Dict[str, Any]]):
    """Command to validate osquery."""
    
    def __init__(self, http_client: HTTPClient, request: List[Dict[str, Any]]):
        self.http_client = http_client
        self.request = request
    
    def execute(self) -> Dict[str, Any]:
        """Execute the validate osquery command."""
        return self.http_client.post("acquisitions/profiles/osquery/validate", json_data=self.request)  # type: ignore 