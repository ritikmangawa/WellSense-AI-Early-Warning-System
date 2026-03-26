import os
import json

metrics_dir = "metrics"

# Load JSON data
try:
    with open(os.path.join(metrics_dir, "metrics_report.json"), "r") as f:
        metrics_report = json.load(f)
except:
    metrics_report = {"Accuracy": 0, "Confusion_Matrix": [[0,0,0],[0,0,0],[0,0,0]]}

try:
    with open(os.path.join(metrics_dir, "training_history.json"), "r") as f:
        training_history = json.load(f)
except:
    training_history = {"loss": [], "mae": []}

try:
    with open(os.path.join(metrics_dir, "accuracy_graph_data.json"), "r") as f:
        accuracy_data = json.load(f)
except:
    accuracy_data = []

# Generate HTML Template
html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ML Metrics Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f4f7f6;
            color: #333;
        }}
        .header {{
            text-align: center;
            padding: 20px 0;
            background: #2b3a42;
            color: white;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
        .metrics-cards {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }}
        .card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            flex: 1;
            margin: 0 10px;
            text-align: center;
            min-width: 150px;
        }}
        .card h3 {{ margin: 0 0 10px 0; color: #777; font-size: 14px; text-transform: uppercase; }}
        .card p {{ margin: 0; font-size: 28px; font-weight: bold; color: #2b3a42; }}
        
        .grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }}
        .chart-container {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }}
        .confusion-matrix table {{
            width: 100%;
            border-collapse: collapse;
            text-align: center;
            margin-top: 20px;
        }}
        .confusion-matrix th, .confusion-matrix td {{
            padding: 15px;
            border: 1px solid #ddd;
        }}
        .confusion-matrix th {{ background: #f8f9fa; }}
        /* heatmap colors placeholder */
        .h-low {{ background: rgba(54, 162, 235, 0.2); }}
        .h-med {{ background: rgba(54, 162, 235, 0.5); }}
        .h-high {{ background: rgba(54, 162, 235, 0.8); color: white; }}
    </style>
</head>
<body>

    <div class="header">
        <h1>Mental Health Predictor - ML Metrics Report</h1>
        <p>Comprehensive overview of model performance and evaluation graphs</p>
    </div>

    <div class="metrics-cards">
        <div class="card">
            <h3>Test Accuracy</h3>
            <p>{metrics_report.get('Accuracy', 0) * 100:.2f}%</p>
        </div>
        <div class="card">
            <h3>R² Score</h3>
            <p>{metrics_report.get('R2_Score', 0):.4f}</p>
        </div>
        <div class="card">
            <h3>Mean Abs. Error (MAE)</h3>
            <p>{metrics_report.get('Mean_Absolute_Error', 0):.4f}</p>
        </div>
        <div class="card">
            <h3>Mean Sqr. Error (MSE)</h3>
            <p>{metrics_report.get('Mean_Squared_Error', 0):.4f}</p>
        </div>
    </div>

    <div class="grid">
        <div class="chart-container">
            <h2>1. Training Loss Curve (MSE & MAE)</h2>
            <p style="font-size:12px; color:#666;">Shows how the model learned over epochs.</p>
            <canvas id="lossChart"></canvas>
        </div>

        <div class="chart-container">
            <h2>2. Actual vs Predicted Stress Levels</h2>
            <p style="font-size:12px; color:#666;">Comparing the model predictions against true risk labels.</p>
            <canvas id="accuracyChart"></canvas>
        </div>

        <div class="chart-container confusion-matrix">
            <h2>3. Confusion Matrix</h2>
            <p style="font-size:12px; color:#666;">Matrix displaying True Positives, False Positives, etc.</p>
            <table id="cmTable">
                <tr>
                    <th></th>
                    <th>Predicted Low (0)</th>
                    <th>Predicted Medium (1)</th>
                    <th>Predicted High (2)</th>
                </tr>
            </table>
        </div>
        
        <div class="chart-container">
            <h2>4. Error Distribution (Residuals)</h2>
            <p style="font-size:12px; color:#666;">Shows the frequency of prediction error magnitudes.</p>
            <canvas id="residualChart"></canvas>
        </div>
    </div>

    <script>
        // Data From Python
        const trainingHistory = {json.dumps(training_history)};
        const accuracyData = {json.dumps(accuracy_data)};
        const confusionMatrix = {json.dumps(metrics_report.get('Confusion_Matrix', [[0,0,0],[0,0,0],[0,0,0]]))};

        // 1. Loss Curve Chart
        const epochs = Array.from({{length: trainingHistory.loss ? trainingHistory.loss.length : 0}}, (_, i) => i + 1);
        new Chart(document.getElementById('lossChart'), {{
            type: 'line',
            data: {{
                labels: epochs,
                datasets: [
                    {{
                        label: 'Training Loss (MSE)',
                        data: trainingHistory.loss,
                        borderColor: '#ff6384',
                        backgroundColor: 'rgba(255, 99, 132, 0.2)',
                        tension: 0.4,
                        fill: true
                    }},
                    {{
                        label: 'Training MAE',
                        data: trainingHistory.mae,
                        borderColor: '#36a2eb',
                        backgroundColor: 'rgba(54, 162, 235, 0.2)',
                        tension: 0.4,
                        fill: true
                    }}
                ]
            }},
            options: {{ responsive: true, scales: {{ y: {{ beginAtZero: true }} }} }}
        }});

        // 2. Actual vs Predicted Chart
        const labels = accuracyData.map(d => d.time_index);
        const actuals = accuracyData.map(d => d.actual);
        const predictions = accuracyData.map(d => d.predicted);
        
        new Chart(document.getElementById('accuracyChart'), {{
            type: 'line',
            data: {{
                labels: Object.keys(labels).length > 0 ? labels.slice(0, 50) : [],
                datasets: [
                    {{
                        label: 'Actual Stress Risk (Scaled)',
                        data: actuals.slice(0, 50),
                        borderColor: '#4bc0c0',
                        backgroundColor: '#4bc0c0',
                        pointRadius: 4,
                        showLine: false
                    }},
                    {{
                        label: 'Predicted Stress Risk',
                        data: predictions.slice(0, 50),
                        borderColor: '#ff9f40',
                        backgroundColor: '#ff9f40',
                        pointRadius: 4,
                        pointStyle: 'crossRot',
                        showLine: false
                    }}
                ]
            }},
            options: {{ responsive: true }}
        }});

        // 3. Render Confusion Matrix Table
        const cmTable = document.getElementById('cmTable');
        const trueLabels = ["Actual Low (0)", "Actual Medium (1)", "Actual High (2)"];
        let maxVal = 0;
        confusionMatrix.forEach(r => r.forEach(v => {{ if(v > maxVal) maxVal = v; }}));
        
        confusionMatrix.forEach((row, i) => {{
            const tr = document.createElement('tr');
            const th = document.createElement('th');
            th.innerText = trueLabels[i];
            tr.appendChild(th);
            
            row.forEach(val => {{
                const td = document.createElement('td');
                td.innerText = val;
                // Heatmap logic
                let ratio = val / (maxVal || 1);
                if(ratio > 0.66) td.className = 'h-high';
                else if(ratio > 0.33) td.className = 'h-med';
                else if(ratio > 0) td.className = 'h-low';
                
                tr.appendChild(td);
            }});
            cmTable.appendChild(tr);
        }});

        // 4. Residuals/Error Histogram
        const residuals = actuals.map((act, i) => act - predictions[i]);
        const bins = [-1, -0.75, -0.5, -0.25, 0, 0.25, 0.5, 0.75, 1];
        const counts = new Array(bins.length-1).fill(0);
        
        residuals.forEach(r => {{
            for(let i=0; i<bins.length-1; i++){{
                if(r >= bins[i] && r < bins[i+1]) {{
                    counts[i]++;
                    break;
                }}
            }}
        }});

        new Chart(document.getElementById('residualChart'), {{
            type: 'bar',
            data: {{
                labels: ['-1 to -0.75', '-0.75 to -0.5', '-0.5 to -0.25', '-0.25 to 0', '0 to 0.25', '0.25 to 0.5', '0.5 to 0.75', '0.75 to 1'],
                datasets: [{{
                    label: 'Error Frequency',
                    data: counts,
                    backgroundColor: '#9966ff',
                }}]
            }},
            options: {{ responsive: true }}
        }});
    </script>
</body>
</html>
"""

report_path = os.path.join(metrics_dir, "ML_Metrics_Dashboard.html")
with open(report_path, "w", encoding="utf-8") as file:
    file.write(html_content)

print(f"✅ Generated standalone Report: {report_path}")
