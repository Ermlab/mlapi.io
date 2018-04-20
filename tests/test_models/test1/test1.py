import logging
import os
from keras.models import load_model
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
from scipy.misc import imread, imresize
import numpy as np

from models.modelController import ModelControllerClass

class CarsClass(ModelControllerClass):
    
    def __init__(self, config, models_folder_path):
        self.__config = config
        self.__models_folder_path = models_folder_path
        self.__model = None
        self.__model_name = config['modelname']
        self.load()

    def load(self):
        DEBUG_T = "[{}] ".format(self.__model_name)

        file_path = os.path.join(self.__models_folder_path, self.__config['modelfile'])
        model = self.__model_name
        #Loading model
        try:
            logging.info(DEBUG_T + "Loading {} model hdf5 file from {}".format(model, file_path))
            self.__model = load_model(file_path)
            logging.info(DEBUG_T + "Successfully loaded {} model.".format(model))
            self.__model.summary()
        except:
            logging.critical(DEBUG_T + "Failed to load {} hdf5 file".format(file_path))
        self.loadLabels()

    def loadLabels(self):
        model = self.__model_name
        #Labels loading
        labels_file_path = os.path.join(self.__models_folder_path, self.__config["labelsfile"])
        labels = []

        with open(labels_file_path, encoding='utf-8', errors='replace') as f:
            for entry in f:
                labels.append(entry)
        # Labels in format "1=first label\n2=second label" etc.
        labels=[labels[i].split('=')[1] for i in range(0,len(labels))] 
        labels=[x.strip() for x in labels]
        self.__labels = labels

    def get_formatted_prediction(self, predictions):
        percentage_string = []
        for prediction in predictions:
        ## Getting 5 labels
            top5_predictions_positions = prediction.argsort()[-5:][::-1]
            top5_predictions = prediction[top5_predictions_positions] * 100
            
            labels = np.array(self.__labels)
            predicted_labels = labels[top5_predictions_positions]    

            percentage_string = []
            for i in range(len(top5_predictions)):
                percentage_string.append("{:30} {:05.3f}%,".format(predicted_labels[i], top5_predictions[i]))
                #TODO:Return JSON
        return percentage_string
    
    def process_input_data(self, data):
        model_name = self.__model_name
        DEBUG_T = "[{}] ".format(model_name)
        if data:
            try:
                image = imread(data, mode='RGB')
            except:
                logging.error(DEBUG_T + "{} could not be loaded".format(data))

            if self.__config["imagesize"]:
                size = int(self.__config["imagesize"])
                image = imresize(image, (size, size))
            else:
                logging.error(DEBUG_T + "Error while resizing {} image.".format(data))
            image = np.array([image], dtype=np.float32)
            image /= 255
            return self.__model.predict(image)


    