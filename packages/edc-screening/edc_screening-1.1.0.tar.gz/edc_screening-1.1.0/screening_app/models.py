from django.db import models
from edc_consent.field_mixins import (
    CitizenFieldsMixin,
    IdentityFieldsMixin,
    PersonalFieldsMixin,
    ReviewFieldsMixin,
    VulnerabilityFieldsMixin,
)
from edc_consent.managers import ConsentObjectsByCdefManager, CurrentSiteByCdefManager
from edc_consent.model_mixins import ConsentModelMixin
from edc_constants.constants import YES
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierModelMixin
from edc_model.models import BaseUuidModel, HistoricalRecords
from edc_sites.model_mixins import SiteModelMixin

from edc_screening.model_mixins import EligibilityModelMixin, ScreeningModelMixin

from .eligibility import MyScreeningEligibility


class SubjectScreening(ScreeningModelMixin, BaseUuidModel):
    thing = models.CharField(max_length=10, null=True)

    def get_consent_definition(self):
        pass


class SubjectScreeningWithEligibility(
    ScreeningModelMixin, EligibilityModelMixin, BaseUuidModel
):
    eligibility_cls = MyScreeningEligibility

    alive = models.CharField(max_length=10, default=YES)

    def get_consent_definition(self):
        pass


class SubjectScreeningWithEligibilitySimple(
    ScreeningModelMixin, EligibilityModelMixin, BaseUuidModel
):
    def get_consent_definition(self):
        pass


class SubjectConsent(
    ConsentModelMixin,
    SiteModelMixin,
    NonUniqueSubjectIdentifierModelMixin,
    IdentityFieldsMixin,
    ReviewFieldsMixin,
    PersonalFieldsMixin,
    CitizenFieldsMixin,
    VulnerabilityFieldsMixin,
    BaseUuidModel,
):
    screening_identifier = models.CharField(
        verbose_name="Screening identifier", max_length=50, unique=True
    )
    history = HistoricalRecords()

    class Meta(ConsentModelMixin.Meta):
        pass


class SubjectConsentV1(SubjectConsent):
    objects = ConsentObjectsByCdefManager()
    on_site = CurrentSiteByCdefManager()

    class Meta:
        proxy = True
