NeuralODE:: code and OpenAPS dataset: https://drive.google.com/drive/folders/1fujR3Zgy97DXKzE79Z7gFEtobmZRcGPb?usp=drive_link

Summery: I use OpenAPS dataset patient1 for training and patient2 for testing the result, the average RMSE is below 10 - most time 6-8 (compare to LSTM average 10), i dont have a precise number because the training require huge amount of time which I only use half of the dataset from patient1 to train and get the rough result.

Notice:
1.  The top of the file where "drive.mount('/content/drive')" is loading google drive to the colab for dataset. If you run on your computer just delete this.
2.  Change the path = "/content/drive/MyDrive/APS/openAPS_data" to your location to the file.
