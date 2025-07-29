from dateutil.relativedelta import relativedelta
from django.test import TestCase, override_settings
from edc_utils import get_utcnow

from edc_protocol.research_protocol_config import ResearchProtocolConfig

opendte = get_utcnow() - relativedelta(years=2)
closedte = get_utcnow() + relativedelta(years=1)


class TestProtocol(TestCase):
    @override_settings(
        EDC_PROTOCOL_STUDY_OPEN_DATETIME=get_utcnow() - relativedelta(years=2),
        EDC_PROTOCOL_STUDY_CLOSE_DATETIME=get_utcnow() + relativedelta(years=1),
    )
    def test_protocol(self):
        self.assertEqual(ResearchProtocolConfig().study_open_datetime.date(), opendte.date())
        self.assertEqual(ResearchProtocolConfig().study_close_datetime.date(), closedte.date())
