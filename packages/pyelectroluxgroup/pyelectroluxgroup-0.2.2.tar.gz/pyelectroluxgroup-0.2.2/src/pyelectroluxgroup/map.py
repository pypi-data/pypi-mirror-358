from typing import Any, Dict


class Area:
    """Class representing a zone in an interactive map."""

    def __init__(self, data: Dict[str, Any]):
        """Initialize the zone with data."""
        self.data = data

    @property
    def id(self) -> str:
        """Return the area ID."""
        return self.data["id"]

    @property
    def name(self) -> str:
        """Return the area name."""
        return self.data["name"]


class Zone(Area):
    """Class representing a zone in an interactive map."""

    def __init__(self, data: Dict[str, Any]):
        """Initialize the zone with data."""
        super().__init__(data)

    @property
    def type(self) -> str:
        """Return the zone type."""
        return self.data["zoneType"]

    @property
    def power_mode(self) -> str:
        """Return the power mode of the zone."""
        return self.data["powerMode"]


class Room(Area):
    """Class representing a room in a memory map."""

    def __init__(self, data: Dict[str, Any]):
        """Initialize the room with data."""
        super().__init__(data)


class Map:
    """Base class for maps for RVCs."""

    def __init__(self, data: Dict[str, Any]):
        """Initialize the map with data."""
        self.data = data

    @property
    def id(self) -> str:
        """Return the map ID."""
        return self.data["id"]

    @property
    def name(self) -> str:
        """Return the map name."""
        return self.data["name"]

    @property
    def areas(self) -> list[Area]:
        return []


class InteractiveMap(Map):
    """Class for interactive maps, used in Pure i8 and i9 RVCs."""

    def __init__(self, data: Dict[str, Any]):
        """Initialize the interactive map with data."""
        super().__init__(data)
        self.zones: list[Area] = [Zone(zone) for zone in data["zones"]]

    @property
    def areas(self) -> list[Area]:
        return list(self.zones)


class MemoryMap(Map):
    """Class for memory maps, used in 700 series RVCs."""

    def __init__(self, data: Dict[str, Any]):
        """Initialize the memory map with data."""
        super().__init__(data)
        self.rooms = [Room(room) for room in data["rooms"]]

    @property
    def areas(self) -> list[Area]:
        return list(self.rooms)
