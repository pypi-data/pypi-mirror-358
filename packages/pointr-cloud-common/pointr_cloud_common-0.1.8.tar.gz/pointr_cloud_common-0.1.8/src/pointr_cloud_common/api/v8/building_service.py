from typing import Dict, Any, List, Optional
import logging

from pointr_cloud_common.dto.v9 import BuildingDTO, LevelDTO
from pointr_cloud_common.dto.v9.validation import ensure_dict, ValidationError
from pointr_cloud_common.api.v8.base_service import BaseApiService, V8ApiError


DEFAULT_GEOMETRY = {
    "type": "Polygon",
    "coordinates": [[[0.0, 0.0], [0.0, 0.001], [0.001, 0.001], [0.001, 0.0], [0.0, 0.0]]],
}


class BuildingApiService(BaseApiService):
    """Service for building-related V8 API operations."""

    def __init__(self, api_service):
        super().__init__(api_service)
        self.logger = logging.getLogger(__name__)

    def _fetch_source_geometry(
        self, fid: str, site_fid: str, source_api_service: Any
    ) -> Optional[Dict[str, Any]]:
        """Fetch geometry for the given building fid from the source API service."""
        try:
            data = source_api_service._make_request(
                "GET", f"api/v8/buildings/{fid}/draft"
            )
            result = data.get("result", data)
            geometry = result.get("geometry")
            if geometry:
                self.logger.info(
                    f"Successfully retrieved geometry for building {fid} from source API"
                )
                return geometry
            self.logger.warning(
                f"No geometry found for building {fid} in source API"
            )
        except Exception as e:
            self.logger.error(
                f"Failed to retrieve geometry for building {fid} from source API: {str(e)}"
            )
        return None

    def _level_from_v8(self, data: Dict[str, Any], site_fid: str, building_fid: str) -> LevelDTO:
        try:
            return LevelDTO(
                fid=str(data.get("levelIndex")),
                name=data.get("levelLongTitle", ""),
                shortName=data.get("levelShortTitle"),
                levelNumber=data.get("levelIndex"),
                typeCode="level-outline",
                sid=site_fid,
                bid=building_fid,
            )
        except ValidationError as e:
            raise V8ApiError(f"Failed to parse level: {str(e)}")

    def _building_from_v8(self, data: Dict[str, Any], site_fid: str) -> BuildingDTO:
        print(f"[DEBUG] Parsing building from V8: site_fid={site_fid}, data={data}")
        levels = [self._level_from_v8(l, site_fid, str(data.get("buildingInternalIdentifier"))) for l in data.get("levels", [])]
        try:
            building_dto = BuildingDTO(
                fid=str(data.get("buildingInternalIdentifier")),
                name=data.get("buildingTitle", ""),
                typeCode="building-outline",
                sid=site_fid,
                bid=data.get("buildingExternalIdentifier"),
                extraData=ensure_dict(data.get("buildingExtraData"), "buildingExtraData"),
                levels=levels,
            )
            print(f"[DEBUG] Created BuildingDTO: fid={building_dto.fid}, name='{building_dto.name}', sid={building_dto.sid}")
            return building_dto
        except ValidationError as e:
            print(f"[DEBUG] Failed to parse building: {str(e)}")
            raise V8ApiError(f"Failed to parse building: {str(e)}")

    def get_buildings(self, site_fid: str) -> List[BuildingDTO]:
        endpoint = f"api/v8/sites/{site_fid}/buildings/draft"
        data = self._make_request("GET", endpoint)
        print(f"[DEBUG] Raw V8 API response for buildings (site_fid={site_fid}): {data}")
        results = data.get("results", []) if isinstance(data, dict) else []
        buildings = [self._building_from_v8(b, site_fid) for b in results]
        print(f"[DEBUG] Parsed {len(buildings)} buildings for site_fid={site_fid}")
        return buildings

    def get_building_by_fid(self, site_fid: str, building_fid: str) -> BuildingDTO:
        endpoint = f"api/v8/buildings/{building_fid}"
        data = self._make_request("GET", endpoint)
        result = data.get("result", data)
        return self._building_from_v8(result, site_fid)

    def create_building(
        self,
        site_fid: str,
        building: BuildingDTO,
        source_api_service: Optional[Any] = None,
    ) -> str:
        geometry = DEFAULT_GEOMETRY
        if source_api_service:
            fetched = self._fetch_source_geometry(building.fid, site_fid, source_api_service)
            if fetched:
                geometry = fetched
        payload = {
            "buildingTitle": building.name,
            "buildingExternalIdentifier": building.bid,
            "buildingExtraData": building.extraData,
            "geometry": geometry,
        }
        endpoint = f"api/v8/sites/{site_fid}/buildings"
        data = self._make_request("POST", endpoint, payload)
        return str(data.get("result", {}).get("buildingInternalIdentifier", ""))


    def update_building(
        self,
        site_fid: str,
        building_fid: str,
        building: BuildingDTO,
        source_api_service: Optional[Any] = None,
    ) -> str:
        geometry = DEFAULT_GEOMETRY
        if source_api_service:
            fetched = self._fetch_source_geometry(building.fid, site_fid, source_api_service)
            if fetched:
                geometry = fetched
        payload = {
            "buildingTitle": building.name,
            "buildingExternalIdentifier": building.bid,
            "buildingExtraData": building.extraData,
            "geometry": geometry,
        }
        endpoint = f"api/v8/buildings/{building_fid}"
        self._make_request("PATCH", endpoint, payload)
        return building_fid
