import typing
import uuid

from results import Result

from currency_convert.domain.agency.entities.agency import (
    Agency,
    AgencyError,
    AgencyNotFoundError,
)


class AgencyRepository(typing.Protocol):
    def create(
        self,
        base: str,
        name: str,
        address: str,
        country: str,
    ) -> Result[uuid.UUID, AgencyError]:
        pass

    def find_by_id(self, agency_id: str) -> Result[Agency, AgencyNotFoundError]:
        pass

    def find_by_name(self, name: str) -> Result[Agency, AgencyNotFoundError]:
        pass

    def find_all(self) -> Result[list[Agency], AgencyError]:
        pass
