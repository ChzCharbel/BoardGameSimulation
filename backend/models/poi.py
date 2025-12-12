from enum import Enum

class POIType(Enum):
    FALSE = "false"
    VICTIM = "victim"

class POI:
    def __init__(self, poi_id, poi_type: POIType, x, y):
        self.id = poi_id
        self.type = poi_type
        self.x = x
        self.y = y
        self.revealed = False
