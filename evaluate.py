import os
import pandas as pd
import numpy as np
import json
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error, accuracy_score, confusion_matrix
from tensorflow.keras.models import load_model

# Setup paths
data_path = "data/student_stress_sleep_screen.csv"
model_path = "model/gru_model.h5"
metrics_dir = "metrics"

if not os.path.exists(metrics_dir):
    os.makedirs(metrics_dir)

print("Loading data...")
df = pd.read_csv(data_path)
df_selected = df[['sleep_hours', 'screen_time_hours', 'study_hours', 'physical_activity', 'stress_level']].copy()

df_selected['physical_activity'] = df_selected['physical_activity'].map({'No': 0, 'Yes': 1})
df_selected['stress_level'] = df_selected['stress_level'].map({'Low': 0, 'Medium': 1, 'High': 2})
df_selected = df_selected.dropna()

scaler = MinMaxScaler()
scaled_data = scaler.fit_transform(df_selected)
df_scaled = pd.DataFrame(scaled_data, columns=df_selected.columns)

def create_sequences(data_array, time_steps=7):
    X, y = [], []
    for i in range(len(data_array) - time_steps):
        X.append(data_array[i : i+time_steps])
        y.append(data_array[i+time_steps][4])
    return np.array(X), np.array(y)

data_matrix = df_scaled.values 
X, y = create_sequences(data_matrix, time_steps=7)

print("Loading model...")
model = load_model(model_path)

print("Predicting...")
predictions = model.predict(X)

# Calculate regression metrics
r2 = r2_score(y, predictions)
mae = mean_absolute_error(y, predictions)
mse = mean_squared_error(y, predictions)

# Calculate accuracy by matching to nearest class (0, 0.5, 1.0)
y_classes = np.round(y * 2)
pred_classes = np.round(predictions.flatten() * 2)
accuracy = accuracy_score(y_classes, pred_classes)

print(f"\n--- Model Metrics ---")
print(f"R2 Score: {r2:.4f}")
print(f"Mean Absolute Error: {mae:.4f}")
print(f"Mean Squared Error: {mse:.4f}")
print(f"Accuracy: {accuracy:.4%}")

# Save Predicted vs Actual last 100 samples to JSON for the frontend
data_out = []
for i in range(1, min(101, len(y) + 1)):
    data_out.append({
        "time_index": i,
        "actual": float(y[-i]),
        "predicted": float(predictions[-i][0])
    })

chart_path = os.path.join(metrics_dir, "accuracy_graph_data.json")
with open(chart_path, "w") as f:
    json.dump(data_out, f, indent=4)
print(f"Saved accuracy graph data to {chart_path}")

# Output summary
cm = confusion_matrix(y_classes, pred_classes, labels=[0., 1., 2.])

metrics_out = {
    "R2_Score": float(r2),
    "Mean_Absolute_Error": float(mae),
    "Mean_Squared_Error": float(mse),
    "Accuracy": float(accuracy),
    "Confusion_Matrix": cm.tolist()
}

with open(os.path.join(metrics_dir, "metrics_report.json"), "w") as f:
    json.dump(metrics_out, f, indent=4)

