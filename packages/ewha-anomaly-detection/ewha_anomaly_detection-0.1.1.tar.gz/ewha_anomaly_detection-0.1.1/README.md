# ewha-db-manager

A Python package for detecting abnormal pedestrian trajectory with LSTM-VAE model.


## How to use

'''python
from ewha_anomaly_detection.anomaly_detection import Anomaly_Detection as ad

weights_path = "/your_directory/vae_lstm_weights.weights.h5"

anmly = ad(df=df, weights_path=weights_path)
anomaly_1, anomaly_2 = anmly.call()
'''

ad.call() automatically predicts (1) the abnormal trajectory IDs from your pedestrian trajectory dataset and (2) the abnormal trajectory ratio for each CCTV road segment from which the trajectories were extracted.

## Requirements

numpy == 1.24.3
pandas
geopandas
shapely
tensorflow

## License
This project is licensed under the JuyeonCho License.

## Contact
whwndus13@naver.com
