# MLAPI.io Documentation

Simple API Framework for serving your **Machine Learning** model.

Don't write glue code for API and Keras model!
We did it for You!


## Getting started

We will show by example how to run Your own project.

Suppose our project is "Cats recognition" - does the picture contain a cat or not?



### 1. Save model

If you use Keras library, the first step is to save model as below:

```python
# import necessary package
import h5py

# Define simple example Keras model
model = Sequential()
(...)
model.save('catsRecognition.h5')
```

After this process you will receive in the main project directory file: catsRecognition.h5.

### 2. Insert Your model into MLAPI

 1. Go to mlapi main directory
 2. ```/API/models/computed```
 3. Create Your own directory name for example "cats"
 4. Insert your model file into folder /cats

### 3. Write config for Your model

```yaml
[CATS]
modelName: cats
modelFullName: Cats Recognition
modelFile: catsRecognition.h5
outputValueType: class_probability
contentType: image

modelControllerClassOverrideFile: cats
modelControllerClassName: CatsClass

```

Save above lines in your ***/cats*** folder as config.ini

### 4. Write Class for Your model


```buildoutcfg

```




## <b> Check our ready models </b>

### Car Recognition

### Polish Sentiment Analysis

