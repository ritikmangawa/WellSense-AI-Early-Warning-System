import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import numpy as np

# 1. Load your real dataset from the data folder
df = pd.read_csv("data/student_stress_sleep_screen.csv")

# 2. Select the most important features based on the columns you provided
# We'll use: sleep, screen time, study hours, physical activity, and stress
df_selected = df[['sleep_hours', 'screen_time_hours', 'study_hours', 'physical_activity', 'stress_level']].copy()

# 3. Convert text (Categorical) columns into numbers so the ML model can understand them
# Map physical_activity: 'No' -> 0, 'Yes' -> 1
df_selected['physical_activity'] = df_selected['physical_activity'].map({'No': 0, 'Yes': 1})

# Map stress_level (Our Prediction Target): 'Low' -> 0, 'Medium' -> 1, 'High' -> 2
df_selected['stress_level'] = df_selected['stress_level'].map({'Low': 0, 'Medium': 1, 'High': 2})

# Drop any rows that might have missing mapping values just in case
df_selected = df_selected.dropna()

print("--- Data Before Scaling ---")
print(df_selected.head(), "\n")

# 4. Normalize the data (Scale everything between 0 and 1)
# Models like GRU perform much better when numbers are small and uniform
scaler = MinMaxScaler()
# Fit and transform the data, then convert back to a dataframe so it's easy to read
scaled_data = scaler.fit_transform(df_selected)
df_scaled = pd.DataFrame(scaled_data, columns=df_selected.columns)

print("--- Data After Scaling ---")
print(df_scaled.head())

print("\n✅ Step 1 (Preprocessing) completed successfully!")

# --- STEP 2: CREATE TIME SEQUENCES ---
# A GRU model doesn't just read "today's data". It needs to read the last X days to predict the future.
print("\n--- Step 2: Creating Time Sequences ---")

def create_sequences(data_array, time_steps=7):
    X, y = [], []
    # data_array is a numpy array. The last column (index 4) is our target 'stress_level'
    for i in range(len(data_array) - time_steps):
        # Grab 7 days of data
        X.append(data_array[i : i+time_steps])
        # The stress level of the *8th* day is what we want to predict
        y.append(data_array[i+time_steps][4])
        
    return np.array(X), np.array(y)

# Convert our Pandas DataFrame to a raw numpy array and create our sequences
data_matrix = df_scaled.values 
X, y = create_sequences(data_matrix, time_steps=7)

print(f"Total sequences created: {len(X)}")
print(f"Shape of X (Input data): {X.shape} => (Samples, Time Steps, Features)")
print(f"Shape of y (Output target): {y.shape} => (Samples,)")
print("✅ Step 2 (Sequences) completed successfully!")

# --- STEP 3: BUILD GRU MODEL ---
import numpy as np
import tensorflow as tf
from sklearn.metrics import accuracy_score
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import GRU, Dense, Dropout

class AccuracyThresholdCallback(tf.keras.callbacks.Callback):
    def __init__(self, X, y, target_accuracy=0.88):
        super().__init__()
        self.X = X
        self.y = y
        self.target_accuracy = target_accuracy

    def on_epoch_end(self, epoch, logs=None):
        predictions = self.model.predict(self.X, verbose=0)
        y_classes = np.round(self.y * 2)
        pred_classes = np.round(predictions.flatten() * 2)
        accuracy = accuracy_score(y_classes, pred_classes)
        print(f" - Custom Accuracy: {accuracy:.4%}")
        if accuracy >= self.target_accuracy:
            print(f"\nReached target accuracy {self.target_accuracy * 100}%! Stopping training.")
            self.model.stop_training = True

print("\n--- Step 3: Building GRU Model ---")
model = Sequential()

# Input shape must match our sequence: (Time Steps=7, Features=5)
model.add(GRU(256, return_sequences=True, input_shape=(7, 5)))
model.add(GRU(128))
model.add(Dense(64, activation='relu'))
model.add(Dense(32, activation='relu'))
# Since our stress target is scaled between 0 and 1, we use sigmoid activation
model.add(Dense(1, activation='sigmoid'))

model.compile(
    optimizer='adam',
    # Since we are predicting a risk score between 0 and 1, we use Mean Squared Error
    loss='mean_squared_error', 
    metrics=['mae']
)

model.summary()
print("✅ Step 3 (Model Architecture) completed successfully!")

# --- STEP 4 & 5: TRAIN AND SAVE MODEL ---
print("\\n--- Step 4: Training the Model ---")
# Train the model for more epochs to improve accuracy, using early stopping if needed
target_acc_callback = AccuracyThresholdCallback(X, y, target_accuracy=0.88)
history = model.fit(X, y, epochs=300, batch_size=16, callbacks=[target_acc_callback])

print("\\n--- Step 5: Saving the Trained Model and History ---")
# Save the model so we can build the API and Frontend!
model.save("model/gru_model.h5")

import json
import os
os.makedirs("metrics", exist_ok=True)
history_dict = {key: [float(val) for val in values] for key, values in history.history.items()}
with open("metrics/training_history.json", "w") as f:
    json.dump(history_dict, f, indent=4)
print("Saved training history to metrics/training_history.json")

print("\\n🎉 ML PIPELINE COMPLETE! Model Saved to model/gru_model.h5")
