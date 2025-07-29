import shutil
import tempfile
from os.path import join as path_join

import torch

from frogml.pytorch import pickle_module as pytorch_pickle_module
from tests.frogml.utils.test_files_tools import given_full_path_to_file
from tests.resources.models.pytorch.pytorch_nn_model import (
    get_train_data,
    get_trained_model,
)


def assert_same_pytorch_model(original_model, loaded_model, train_data_input):
    original_state = original_model.state_dict()
    loaded_state = loaded_model.state_dict()
    for key in original_state:
        assert torch.equal(original_state[key], loaded_state[key])

    predictions_original_model = original_model(train_data_input)
    predictions_loaded_model = loaded_model(train_data_input)

    assert torch.equal(predictions_original_model, predictions_loaded_model)


def test_pickle_module():
    data_path = "../../../tests/resources/models/pytorch/pima-indians-diabetes.data.csv"
    full_full_path = given_full_path_to_file(file_name=data_path)
    train_data_input, train_data_output = get_train_data(full_full_path)
    original_model = get_trained_model(train_data_input, train_data_output)

    tempdir = tempfile.mkdtemp()
    full_model_path = path_join(tempdir, "model.pth")

    torch.save(
        obj=original_model, f=full_model_path, pickle_module=pytorch_pickle_module
    )

    loaded_model = torch.load(f=full_model_path, pickle_module=pytorch_pickle_module)

    shutil.rmtree(tempdir)

    assert_same_pytorch_model(original_model, loaded_model, train_data_input)
