import os
from typing import Any
from jinja2 import Template

HTML_REPORT_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>AutoDS — Exploratory Data Analysis Report</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 30px; }
    .container { max-width: 1100px; margin: 0 auto; background: #1e293b; border-radius: 12px; padding: 40px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }
    h1 { color: #38bdf8; border-bottom: 2px solid #334155; padding-bottom: 15px; margin-top: 0; }
    h2 { color: #818cf8; margin-top: 30px; border-bottom: 1px solid #334155; padding-bottom: 8px; }
    .card { background: #0f172a; padding: 20px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #334155; }
    table { width: 100%; border-collapse: collapse; margin-top: 15px; }
    th, td { text-align: left; padding: 12px; border-bottom: 1px solid #334155; }
    th { background: #334155; color: #38bdf8; }
    .badge { background: #0284c7; color: white; padding: 4px 10px; border-radius: 9999px; font-size: 0.85em; font-weight: bold; }
    .insights-list { background: #1e1b4b; border-left: 4px solid #6366f1; padding: 15px 20px; border-radius: 4px; margin-top: 15px; }
    .charts-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-top: 20px; }
    .chart-card { background: #0f172a; padding: 15px; border-radius: 8px; text-align: center; border: 1px solid #334155; }
    .chart-card img { max-width: 100%; height: auto; border-radius: 6px; }
  </style>
</head>
<body>
  <div class="container">
    <h1>AutoDS — Exploratory Data Analysis Report</h1>
    <p><strong>Dataset ID:</strong> {{ dataset_id }}</p>
    <p><strong>Generated At:</strong> {{ generated_at }}</p>

    <h2>1. Executive Summary & AI Insights</h2>
    <div class="card">
      <p>{{ summary }}</p>
      
      {% if insights.get('key_findings') %}
      <h3>Key Findings</h3>
      <div class="insights-list">
        <ul>
          {% for finding in insights.get('key_findings', []) %}
          <li>{{ finding }}</li>
          {% endfor %}
        </ul>
      </div>
      {% endif %}

      {% if insights.get('business_recommendations') %}
      <h3>Recommendations</h3>
      <div class="insights-list">
        <ul>
          {% for rec in insights.get('business_recommendations', []) %}
          <li>{{ rec }}</li>
          {% endfor %}
        </ul>
      </div>
      {% endif %}
    </div>

    <h2>2. Dataset Overview & Basic Statistics</h2>
    <div class="card">
      <table>
        <tr><th>Metric</th><th>Value</th></tr>
        <tr><td>Total Rows</td><td>{{ statistics.basic.row_count }}</td></tr>
        <tr><td>Total Columns</td><td>{{ statistics.basic.column_count }}</td></tr>
        <tr><td>Duplicate Rows</td><td>{{ statistics.basic.duplicate_count }}</td></tr>
      </table>
    </div>

    <h2>3. Numeric Feature Statistics</h2>
    <div class="card">
      <table>
        <thead>
          <tr>
            <th>Column</th>
            <th>Mean</th>
            <th>Median</th>
            <th>Std Dev</th>
            <th>Min</th>
            <th>Max</th>
            <th>Skewness</th>
          </tr>
        </thead>
        <tbody>
          {% for col, s in statistics.numeric.items() %}
          <tr>
            <td><strong>{{ col }}</strong></td>
            <td>{{ s.mean }}</td>
            <td>{{ s.median }}</td>
            <td>{{ s.std }}</td>
            <td>{{ s.min }}</td>
            <td>{{ s.max }}</td>
            <td>{{ s.skewness }}</td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>

    <h2>4. Outlier Analysis (IQR Method)</h2>
    <div class="card">
      <table>
        <thead>
          <tr>
            <th>Column</th>
            <th>Q1 (25%)</th>
            <th>Q3 (75%)</th>
            <th>IQR</th>
            <th>Outliers Count</th>
            <th>Outliers %</th>
          </tr>
        </thead>
        <tbody>
          {% for col, o in outliers.items() %}
          <tr>
            <td><strong>{{ col }}</strong></td>
            <td>{{ o.q1 }}</td>
            <td>{{ o.q3 }}</td>
            <td>{{ o.iqr }}</td>
            <td><span class="badge">{{ o.outlier_count }}</span></td>
            <td>{{ o.outlier_percentage }}%</td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>

    {% if charts %}
    <h2>5. Visualizations & Distributions</h2>
    <div class="charts-grid">
      {% for name, rel_path in charts.items() %}
      <div class="chart-card">
        <h4>{{ name }}</h4>
        <img src="{{ charts_base_url }}/{{ rel_path }}" alt="{{ name }}" />
      </div>
      {% endfor %}
    </div>
    {% endif %}

    <footer style="margin-top: 50px; text-align: center; color: #64748b; font-size: 0.85em;">
      Report generated automatically by AutoDS AI Engine.
    </footer>
  </div>
</body>
</html>
"""


def generate_html_eda_report(
    dataset_id: str,
    summary: str,
    statistics: dict[str, Any],
    outliers: dict[str, Any],
    charts: dict[str, Any],
    insights: dict[str, Any],
    generated_at: str,
    output_report_path: str,
    charts_base_url: str = "../charts",
) -> str:
    """Renders Jinja2 template and writes eda_report.html to output_report_path."""
    os.makedirs(os.path.dirname(output_report_path), exist_ok=True)
    template = Template(HTML_REPORT_TEMPLATE)

    # Adjust relative chart URLs for html view
    charts_url = f"../charts/{dataset_id}"

    html_content = template.render(
        dataset_id=dataset_id,
        summary=summary,
        statistics=statistics,
        outliers=outliers,
        charts=charts,
        insights=insights,
        generated_at=generated_at,
        charts_base_url=charts_url,
    )

    with open(output_report_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    return output_report_path
