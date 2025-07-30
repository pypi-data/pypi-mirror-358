from pydantic import BaseModel, ConfigDict, Field

class MaleoClientConfigurations(BaseModel):
    key: str = Field(..., description="Client's key")
    name: str = Field(..., description="Client's name")
    url: str = Field(..., description="Client's URL")

class MaleoClientsConfigurations(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    telemetry: MaleoClientConfigurations = Field(..., description="MaleoTelemetry client's configuration")
    metadata: MaleoClientConfigurations = Field(..., description="MaleoMetadata client's configuration")
    identity: MaleoClientConfigurations = Field(..., description="MaleoIdentity client's configuration")
    access: MaleoClientConfigurations = Field(..., description="MaleoAccess client's configuration")
    workshop: MaleoClientConfigurations = Field(..., description="MaleoWorkshop client's configuration")
    soapie: MaleoClientConfigurations = Field(..., description="MaleoSOAPIE client's configuration")
    medix: MaleoClientConfigurations = Field(..., description="MaleoMedix client's configuration")
    dicom: MaleoClientConfigurations = Field(..., description="MaleoDICOM client's configuration")
    scribe: MaleoClientConfigurations = Field(..., description="MaleoScribe client's configuration")
    cds: MaleoClientConfigurations = Field(..., description="MaleoCDS client's configuration")
    imaging: MaleoClientConfigurations = Field(..., description="MaleoImaging client's configuration")
    mcu: MaleoClientConfigurations = Field(..., description="MaleoMCU client's configuration")