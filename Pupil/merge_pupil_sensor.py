import pandas as pd
import datetime

# ---- Load data ----
gaze_df = pd.read_csv('/home/rounak/recordings/2025_05_12/000/exports/000/surfaces/gaze_positions_on_surface_Valance_Arousal.csv')
# sensor_df = pd.read_csv('/home/rounak/CODE/Third_quadrant_prediction orgnl/signals/signals_data.csv')

# ---- Load sensor data without headers ----
sensor_columns = ['millis', 'GSR_sensorValue', 'HR_sensorValue', 'epoch_ms', 'datetime_str']
sensor_df = pd.read_csv(
    '/home/rounak/CODE/Third_quadrant_prediction orgnl/signals/signals_data.csv',
    names=sensor_columns
)

# ---- Define constants from info.player.json ----
start_time_system = 1747033587.924104
start_time_synced = 1116530.305898629
offset = start_time_system - start_time_synced

# ---- Convert gaze timestamps to real datetime ----
gaze_df['gaze_system_ts'] = gaze_df['gaze_timestamp'] + offset
gaze_df['datetime'] = pd.to_datetime(gaze_df['gaze_system_ts'], unit='s')

# ---- Convert sensor millis to real datetime ----
sensor_df = sensor_df.rename(columns={'millis()': 'millis'})
sensor_df['system_ts'] = start_time_system + (sensor_df['millis'] / 1000.0)
sensor_df['datetime'] = pd.to_datetime(sensor_df['system_ts'], unit='s')

# ---- Sort both by datetime ----
gaze_df = gaze_df.sort_values('datetime')
sensor_df = sensor_df.sort_values('datetime')

# ---- Merge on nearest timestamps ----
merged_df = pd.merge_asof(gaze_df, sensor_df, on='datetime', direction='nearest', tolerance=pd.Timedelta(milliseconds=100))

# ---- Save or view result ----
merged_df.to_csv('merged_gaze_sensor.csv', index=False)
print(merged_df.head())
