import abc
import logging
#TODO: Create a metaclass forbidding incorrect implementation
class ModelControllerClass:
    '''Abstract class that every particular model-specific python file should inherit from in order to load the model.
    
    Attributes
    ----------
    __config : dict
        Config loaded by ModelsControllerClass through ConfigParser
    __model : Keras, Tensorflow or Pycharm format model
        Loaded model
    __models_folder_path : str
        Path to folder containing config.ini of the model.
    __model_name : str
        Name of the loaded model.

    Methods
    -------
    load
    process_input_data
    get_formatted_prediction
    feed
    '''

    __metaclass__ = abc.ABCMeta
    def __init__(self, config, models_folder_path):
        self.__config = config
        self.__models_folder_path = models_folder_path
        self.__model = None
        self.__model_name = config['modelname']
        self.load()
        
    @abc.abstractmethod
    def load(self):
        '''Abstract method for loading models.
        '''
        raise Exception("load not implemented")
    
    @abc.abstractmethod
    def process_input_data(self, data):
        '''Abstract method for processing input data to predict.

        Returns
        -------
        str 
            Models output.
        '''
        raise Exception("process_input_data not implemented")
    
    @abc.abstractmethod
    def get_formatted_prediction(self, prediction):
        '''Abstract method that returns beautified string to send to client

        Parameters
        ----------
        prediction : predictions returned from the model

        Returns
        -------
        str
            pre-formatted string
        '''
        raise Exception("get_formatted_prediction not implemented")
    
    @abc.abstractmethod
    def feed(self, data):
        '''Abstract method returning preformatted prediction on given `data`.

        Parameters
        ----------
        data : str or MultiDict
            Data that comes from the client passed by ModelsHolder's sendRequest method.
        
        Returns
        -------
        str 
            Preformatted prediction
        '''
        data = self.process_input_data(data)
        return self.get_formatted_prediction(data)
        # raise Exception("feed() not implemented")

    __lt__ = __gt__ = load