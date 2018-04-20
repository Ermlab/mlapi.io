import logging
from unittest import TestCase

from models.modelsHolder import ModelsHolderClass

class TestModelsHolder(TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        MODELS_DIR = "./tests/test_models"
        self.__mhc = ModelsHolderClass(MODELS_DIR)
    
    def test_instance_is_initialized(self):
        assert self.__mhc
    
    def test_models_are_loaded(self):
        assert len(self.__mhc.getAvailableModels()) > 0
    
    def test_models_configs_are_loaded(self):
        assert self.__mhc.getModelsConfigs()

    def test_models_config_contains_entries(self):
        logging.debug(self.__mhc.getModelsConfigs())
        config = self.__mhc.getModelsConfigs()['test1']
        assert config['modelname'] == "test1"
        assert config['modelfullname'] == 'Car recognition'
        assert config['modelfile'] == "test1.model"
        assert config['outputvaluetype'] == "class_probability"
        assert config['contenttype'] == "image"
        assert config['description'] == "Make an authenticated POST request for predicting the image. POST binary file with proper header or { 'image' : 'BASE64 image' }"
        assert config['modelcontrollerclassoverridefile'] == "test1"
        assert config['modelcontrollerclassname'] == "CarsClass"
        assert config['imagesize'] == "255"
        assert config['labelsfile'] == "test1.labels"
    
    def test_model_responds_to_a_request(self):
        test_image = "tests/test_models/test1/55555.png"
        response = self.__mhc.sendRequest('test1', test_image)
        assert response and '%' in response[0]

    def test_model_with_bad_class_implementation_raises_exception(self):
        test_image = "tests/test_models/test1/55555.png"
        try:
            response = self.__mhc.sendRequest('test2', test_image)
            assert False
        except Exception:
            assert True

    def test_model_without_config_does_not_throw_exception(self):
        assert 'test3' not in self.__mhc.getModelsConfigs()