import configparser
import os
import logging
import inspect
from importlib import import_module
from mlapi.shellColors import ShellColors


DEFAULT_CONFIG_NAME = "config.ini"
DEBUG_T = ShellColors.RED + "[MODELS_HOLDER] " + ShellColors.ENDC

# class StreamResponderClass:
#     # Defining behavior for `with` function
#     def __enter__(self):
#         print("Processing the request")
#         return self.__data
#     def __exit__(self, a,b,c):
#         return
#     def __init__(self, data):
#         self.__data = data
        
class ModelsHolderClass:
    '''Class that loads and holds in memory all models for further predictions.

    Attributes
    ---------
    __configParser : ConfigParser()
        Instance of config parser for loading configs that come with models.
    __config : dict
        Dictionary that contains entries of configs of every model. {'model_no_1' : {'arg':1, 'arg2':2}}
    __models : list
        List of strings with model names to load.
    __model_instance_holder : dict
        A dictionary containing instances of per-model specific classes (inheriting from the base ModelController class)
    
    Methods
    -------
    sendRequest : invokes the feed() function defined in ModelController class (which can be overriden) and returns it's respond
    getAvailableModels
    getModelsConfigs
    
    '''

    def __init__(self, models_directory):
        logging.info(DEBUG_T + "INITIALIZING")

        self.__configParser = configparser.ConfigParser()
        self.__config = {}
        self.__models = None
        self.__model_instances_holder = {}
        self.__models_directory = models_directory

        self.__loadAllModels()
    def __configSectionMap(self, section):
        '''Returns a dictionary of every config entry for given section i.e. model name.
        '''

        dict1 = {}
        options = self.__configParser.options(section)
        for option in options:
            try:
                dict1[option] = self.__configParser.get(section, option)
                if dict1[option] == -1:
                    logging.debug(DEBUG_T + "skip: {}".format(option))
            except:
                logging.warning(DEBUG_T + "__configSectionMap() exception on {}!".format(option))
                dict1[option] = None
        self.__config[section.lower()] = dict1

    def __loadAllModels(self):
        '''Loads all models found in API/models/computed folder.
        Every model should by in its own directory named with the models shortened name.
        '''

        models_dir_path = os.path.abspath(self.__models_directory)
        logging.info(DEBUG_T + "Loading models from {}".format(models_dir_path))
        models = [x for x in os.listdir(models_dir_path) if os.path.isdir(os.path.join(models_dir_path, x))]
        for model in models:
            model_path = os.path.join(models_dir_path, model)
            if DEFAULT_CONFIG_NAME in os.listdir(model_path):
                config_path = os.path.join(model_path, DEFAULT_CONFIG_NAME)
                logging.debug(config_path)
                
                #Loading config.ini
                try:
                    self.__configParser.read(config_path)
                except:
                    logging.critical(DEBUG_T + 'ERROR WHILE READING MODELS CONFIG - {}'.format(model))
                    models.remove(model)
                
                for s in self.__configParser.sections():
                    self.__configSectionMap(s)
                logging.debug(DEBUG_T + "Loaded config:")
                logging.debug("\t" + str(self.__config))
                
                file_path = os.path.join(model_path, self.__config[model]["modelfile"])
                models_modules_path = '.'.join([x for x in self.__models_directory.split('/') if x and x != '.'])
                logging.debug(models_modules_path)

                override_file_name = self.__config[model]['modelcontrollerclassoverridefile']
                module_path = '.'.join([models_modules_path, model, override_file_name])
                module = import_module(module_path)

                class_name = self.__config[model]['modelcontrollerclassname']

                
                overriding_class = getattr(module, class_name)
                if inspect.isclass(overriding_class):
                    logging.debug("There is {} class for {} model".format(overriding_class.__name__, model))

                logging.info(DEBUG_T + "Loading {} model".format(model))
                self.__model_instances_holder[model.lower()] = overriding_class(self.__config[model], model_path)
                
            else:
                logging.warning(DEBUG_T + 'No config.ini file for {} model'.format(model))
                models.remove(model)
        self.__models = models

    def sendRequest(self, model_name, data):
        '''Invokes the ModelController's feed method that returns models prediction.

        Parameters
        ----------
        model_name : str
            Name of the model to use.
        data : MultiDict or str
            Data sent by the client to pass to the ModelController.
        
        Returns
        -------
        str
            Printable string ready to view / send to client. Prediction results or error message.
        '''
        
        logging.debug(self.__model_instances_holder)
        output = self.__model_instances_holder[model_name].feed(data)
        # return StreamResponderClass(output)
        return output

    def getAvailableModels(self):
        '''Returns loaded and available models.
        '''
        return self.__models
    
    def getModelsConfigs(self):
        '''Get all models configs.

        Returns
        -------
        dict
        '''
        return self.__config
