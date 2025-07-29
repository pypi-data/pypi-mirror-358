from chap_core.api import forecast
import pytest
from chap_core.util import docker_available
from chap_core.cli import sanity_check_model


@pytest.mark.skipif(not docker_available(), reason="Docker not available")
@pytest.mark.skip(reason="Failing on CI")
def test_forecast_github_model():
    repo_url = "https://github.com/knutdrand/external_rmodel_example.git"
    results = forecast("external", "hydromet_5_filtered", 12, repo_url)
