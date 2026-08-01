import os
from typing import Any
from jinja2 import Template

EVALUATION_REPORT_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>AutoDS — Model Evaluation Report</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 30px; }
    .container { max-width: 1100px; margin: 0 auto; background: #1e293b; border-radius: 12px; padding: 40px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }
    h1 { color: #38bdf8; border-bottom: 2px solid #334155; padding-bottom: 15px; margin-top: 0; }
    h2 { color: #818cf8; margin-top: 30px; border-bottom: 1px solid #334155; padding-bottom: 8px; }
    .card { background: #0f172a; padding: 20px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #334155; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 15px; }
    .metric-box { background: #1e293b; padding: 15px; border-radius: 6px; border-left: 4px solid #38bdf8; text-align: center; }
    .metric-value { font-size: 1.8em; font-weight: bold; color: #38bdf8; }
    .metric-label { font-size: 0.85em; color: #94a3b8; text-transform: uppercase; margin-top: 5px; }
    table { width: 100%; border-collapse: collapse; margin-top: 15px; }
    th, td { text-align: left; padding: 12px; border-bottom: 1px solid #334155; }
    th { background: #334155; color: #38bdf8; }
  </style>
</head>
<body>
  <div class="container">
    <h1>AutoDS — Model Evaluation Report</h1>
    <p><strong>Dataset ID:</strong> {{ dataset_id }}</p>
    <p><strong>Algorithm:</strong> {{ algorithm }}</p>
    <p><strong>Problem Type:</strong> {{ problem_type }}</p>
    <p><strong>Generated At:</strong> {{ generated_at }}</p>

    <h2>1. Performance Metrics Overview</h2>
    <div class="card">
      <div class="grid">
        {% for k, v in metrics.items() %}
        {% if k != 'confusion_matrix' and k != 'cross_validation' %}
        <div class="metric-box">
          <div class="metric-value">{{ v }}</div>
          <div class="metric-label">{{ k.replace('_', ' ') }}</div>
        </div>
        {% endif %}
        {% endfor %}
      </div>
    </div>

    {% if metrics.get('cross_validation') %}
    <h2>2. Cross Validation (5-Fold)</h2>
    <div class="card">
      <p><strong>CV Mean Score:</strong> {{ metrics.cross_validation.mean }} &plusmn; {{ metrics.cross_validation.std }}</p>
      <p><strong>Folds:</strong> {{ metrics.cross_validation.folds }}</p>
    </div>
    {% endif %}

    <h2>3. Top Feature Importances & SHAP Values</h2>
    <div class="card">
      <table>
        <thead>
          <tr>
            <th>Feature Name</th>
            <th>Importance Score</th>
            <th>SHAP Value</th>
          </tr>
        </thead>
        <tbody>
          {% for col, score in feature_importance.items() %}
          <tr>
            <td>{{ col }}</td>
            <td>{{ score }}</td>
            <td>{{ shap_values.get(col, 'N/A') }}</td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
  </div>
</body>
</html>
"""


def generate_html_evaluation_report(
    dataset_id: str,
    algorithm: str,
    problem_type: str,
    metrics: dict[str, Any],
    feature_importance: dict[str, Any],
    shap_values: dict[str, Any],
    generated_at: str,
    output_report_path: str,
) -> str:
    os.makedirs(os.path.dirname(output_report_path), exist_ok=True)
    template = Template(EVALUATION_REPORT_TEMPLATE)

    html_content = template.render(
        dataset_id=dataset_id,
        algorithm=algorithm,
        problem_type=problem_type,
        metrics=metrics,
        feature_importance=feature_importance,
        shap_values=shap_values,
        generated_at=generated_at,
    )

    with open(output_report_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    return output_report_path
