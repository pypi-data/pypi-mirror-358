from edc_consent import site_consents
from edc_consent.consent_definition import ConsentDefinition
from edc_protocol.research_protocol_config import ResearchProtocolConfig

consent_v1 = ConsentDefinition(
    "screening_app.subjectconsentv1",
    start=ResearchProtocolConfig().study_open_datetime,
    end=ResearchProtocolConfig().study_close_datetime,
    gender=["M", "F"],
    version="1",
    age_min=16,
    age_max=64,
    age_is_adult=18,
)

site_consents.register(consent_v1)
