from chap_core.models.utils import (
    get_model_from_directory_or_github_url,
)
from .estimators import sanity_check_estimator


def sanity_check_external_model(folder_path: str):
    model = get_model_from_directory_or_github_url(folder_path, run_dir_type="latest")
    sanity_check_estimator(model)


def sanity_check_cli(train_method, train_dataset, model_path, train_filename):
    train_dataset.to_csv(train_filename)
    train_method(train_filename, model_path)
