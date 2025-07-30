from typing import List, Dict, Any
from urllib.parse import urlparse
from datetime import datetime

class VistockValidator:
    REQUIRED_FIELDS = {
        'code', 'date', 'time', 'floor', 'type', 'basicPrice', 'ceilingPrice',
        'floorPrice', 'open', 'high', 'low', 'close', 'average', 'adOpen',
        'adHigh', 'adLow', 'adClose', 'adAverage', 'nmVolume', 'nmValue',
        'ptVolume', 'ptValue', 'change', 'adChange', 'pctChange'
    }

    @staticmethod
    def validate_url(url: str) -> bool:
        try:
            parsed = urlparse(url)
            return all([parsed.scheme, parsed.netloc])
        
        except Exception:
            return False

    @staticmethod
    def validate_url_with_domain(url: str, domain: str) -> bool:
        try:
            parsed = urlparse(url)
            if parsed.scheme in ('http', 'https') and parsed.hostname and parsed.hostname.endswith(domain):
                return True
            else:
                return False
            
        except Exception:
            return False    
        
    @staticmethod
    def validate_date_format(date_str: str, date_format: str = '%Y-%m-%d') -> bool:        
        try:
            datetime.strptime(date_str, date_format)
            return True
        
        except ValueError:
            return False
        
    @staticmethod
    def validate_date_range(start_date: str, end_date: str, date_format: str = '%Y-%m-%d') -> bool:
        if not (VistockValidator.validate_date_format(start_date, date_format) and 
                VistockValidator.validate_date_format(end_date, date_format)):
            return False
        
        start_dt = datetime.strptime(start_date, date_format)
        end_dt = datetime.strptime(end_date, date_format)
        
        return start_dt <= end_dt
    
    @staticmethod
    def validate_resolution(resolution: str) -> bool:
        valid_resolutions = {'day', 'week', 'month', 'year'}
        return resolution in valid_resolutions if resolution else True
    
    @staticmethod
    def validate_json_data(data: List[Dict[str, Any]]) -> bool:
        if not isinstance(data, list):
            return False
        
        for entry in data:
            if not isinstance(entry, dict):
                return False
            
            missing_fields = VistockValidator.REQUIRED_FIELDS - entry.keys()
            if missing_fields:
                return False
            
        return True
        