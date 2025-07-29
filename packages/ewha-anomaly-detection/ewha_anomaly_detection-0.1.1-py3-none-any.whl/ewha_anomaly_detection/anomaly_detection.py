"""Anomaly_detection.py"""


# --- import packages ---
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString
from tensorflow.keras import layers, models, backend as K
import tensorflow as tf


class VAE_LossLayer(layers.Layer):
    def __init__(self):
        super().__init__()

    def call(self, input):
        x, x_decoded, z_mean, z_log_var = input
        recon_loss = tf.reduce_mean(tf.reduce_sum(tf.keras.losses.mse(x, x_decoded), axis=1))
        kl_loss = -0.5 * tf.reduce_mean(tf.reduce_sum(1 + z_log_var - tf.square(z_mean) - K.exp(z_log_var), axis=-1))
        self.add_loss(recon_loss + kl_loss)
        return x_decoded


class vae_lstm_model(models.Model):
    def __init__(self, timesteps, input_dim, latent_dim):
        super().__init__()
        self.timesteps = timesteps
        self.input_dim = input_dim
        self.latent_dim = latent_dim

        # Define layers in __init__
        self.encoder_lstm = layers.LSTM(self.latent_dim)
        self.z_mean_dense = layers.Dense(self.latent_dim)
        self.z_log_var_dense = layers.Dense(self.latent_dim)
        self.sampling_layer = layers.Lambda(self.sampling)

        self.repeat = layers.RepeatVector(self.timesteps)
        self.decoder_lstm = layers.LSTM(self.input_dim, return_sequences=True)

    def sampling(self, args):
        z_mean, z_log_var = args
        epsilon = K.random_normal(shape=(K.shape(z_mean)[0], K.int_shape(z_mean)[1]))
        return z_mean + K.exp(0.5 * z_log_var) * epsilon

    def call(self, inputs):
        encoded = self.encoder_lstm(inputs)
        z_mean = self.z_mean_dense(encoded)
        z_log_var = self.z_log_var_dense(encoded)
        z = self.sampling_layer([z_mean, z_log_var])
        decoded = self.decoder_lstm(self.repeat(z))
        outputs = VAE_LossLayer()([inputs, decoded, z_mean, z_log_var])
        return outputs


class extract_anomaly(layers.Layer):
    def __init__(self, df, timesteps, input_dim, latent_dim, weights_path):
        super().__init__()
        self.df = df
        self.timesteps = timesteps
        self.vae = vae_lstm_model(timesteps, input_dim, latent_dim)
        self.vae(tf.zeros((1, timesteps, input_dim)))
        self.vae.compile(optimizer='adam')
        self.vae.load_weights(weights_path)    

    # --- 3. 재구성 오류 계산 함수 ---
    def calc_reconstruction_errors(self, df_group):
        df_group = df_group.sort_values('dtct_dt').reset_index(drop=True)
        features = df_group[['acceleration', 'angular_difference', 'direction', 'speed']].values
        n = len(features)
        if n < self.timesteps:
            return pd.Series([np.nan]*n, index=df_group.index)

        errors = [np.nan]*(self.timesteps-1)
        for i in range(n - self.timesteps + 1):
            seq = features[i:i+self.timesteps][np.newaxis, :, :]
            recon = self.vae.predict(seq, verbose=0)
            mse = np.mean(np.square(seq - recon))
            errors.append(mse)
        return pd.Series(errors, index=df_group.index)
    
    def create_linestring(self, df_group):
        points = df_group.sort_values('dtct_dt')[['lon','lat']].values
        return LineString(points)

    def get_representative_time(self, df_group):
        return df_group['dtct_dt'].min()

    def get_representative_cctv(self, df_group):
        return df_group['snr_id'].mode().iloc[0]

    def call(self):
        self.df = self.df.reset_index(drop=True)

        # --- 1. reconstruction_error 계산 ---
        recon_error_series = self.df.groupby('traj_id').apply(
            self.calc_reconstruction_errors
        ).reset_index()
        recon_error_series.columns = ['traj_id', 'row_index', 'reconstruction_error']

        # --- 2. 병합하여 reconstruction_error 붙이기 ---
        self.df = self.df.reset_index().rename(columns={'index': 'row_index'})
        self.df = pd.merge(self.df, recon_error_series, on=['traj_id', 'row_index'], how='left')
        self.df = self.df.sort_values('row_index').drop(columns=['row_index'])

        # --- 5. traj_id별 재구성 오류 합산 및 이상 여부 판단 ---
        error_sum = self.df.dropna(subset=['reconstruction_error']).groupby('traj_id')['reconstruction_error'].sum().reset_index()
        threshold = error_sum['reconstruction_error'].quantile(0.99)
        error_sum['Anomaly'] = (error_sum['reconstruction_error'] >= threshold).astype(int)
        anomalous_traj_ids = error_sum.loc[error_sum['Anomaly'] == 1, 'traj_id'].values

        traj_groups = self.df.groupby('traj_id')
        records = []
        for traj_id, group in traj_groups:
            geom = self.create_linestring(group)
            time = self.get_representative_time(group)
            cctv = self.get_representative_cctv(group)
            anomaly_flag = 1 if traj_id in anomalous_traj_ids else 0
            records.append({
                'Traj_id': traj_id,
                'Geometry': geom,
                'time': time,
                'Anomaly': anomaly_flag,
                'CCTV_ID': cctv
            })
        anomal_1 = gpd.GeoDataFrame(records, geometry='Geometry')
        return anomal_1


class Anomaly_Detection(layers.Layer):
    def __init__(self, df, weights_path, timesteps=3, input_dim=4, latent_dim=16):
        super().__init__()
        self.extract_anomaly = extract_anomaly(df, timesteps, input_dim, latent_dim, weights_path)

    def call(self):
        anomal_1 = self.extract_anomaly.call()
        anomal_1['time'] = anomal_1['time'].dt.floor('h')

        grouped = anomal_1.groupby(['CCTV_ID', 'time']).agg(
            total_num=('Traj_id', 'count'),
            anomaly_num=('Anomaly', 'sum')
        ).reset_index()

        grouped['ratio'] = grouped['anomaly_num'] / grouped['total_num']

        anomal_2 = grouped[['CCTV_ID', 'time', 'total_num', 'anomaly_num', 'ratio']]

        # --- 8. 인덱스 초기화 ---
        anomal_1 = anomal_1.reset_index(drop=True)
        anomal_2 = anomal_2.reset_index(drop=True)

        return anomal_1, anomal_2