# AutoDS - Platform Suggestions and Improvements

Based on the recent production audit and the current state of the platform, here are several suggestions, potential improvements, and future-proofing ideas for AutoDS.

## 1. Feature Enhancements
- **Multi-Model Comparison View**: Expand the AutoML results to show a detailed side-by-side comparison (Leaderboard) of all trained models, not just the best one.
- **Model Export Formats**: Allow downloading trained models in **ONNX** format, which provides better cross-platform compatibility and faster inference in production environments compared to `joblib`.
- **Time-Series Forecasting**: Introduce support for time-series tasks. Currently, the system excels at tabular classification and regression.
- **PDF Report Generation**: Add an option to export the EDA and AI Analysis reports as PDF files, in addition to the current HTML/JSON formats.
- **Advanced Data Imputation**: Upgrade the data cleaning step to include advanced imputation methods (like KNN Imputer or Iterative Imputer) for better handling of missing data in complex datasets.

## 2. Performance and Scalability
- **SHAP Value Optimization**: Calculating SHAP values for tree-based models (like XGBoost) can be computationally expensive on large datasets. Consider implementing background sampling (e.g., calculating SHAP on a representative subset of 1,000 rows) to keep the UI responsive.
- **Chunked File Uploads**: For very large CSV/datasets, implement chunked uploads to prevent memory spikes and timeout errors during the initial dataset ingestion.
- **Database Partitioning**: As user projects and datasets grow, consider table partitioning in PostgreSQL for the datasets/features tables to maintain query performance.

## 3. UI/UX Improvements
- **Interactive Visualizations**: Transition from base64-embedded Matplotlib images in the frontend to a fully interactive charting library like **Plotly.js** or **Recharts**. This allows users to hover for exact values, zoom, and pan across their data.
- **Real-time WebSockets**: Replace any polling mechanisms for long-running tasks (like AutoML training or AI analysis generation) with WebSockets or Server-Sent Events (SSE) for instant UI updates.
- **Dataset Versioning**: Allow users to save multiple cleaned versions of the same raw dataset and switch between them without overwriting.

## 4. Security and Robustness
- **API Rate Limiting**: Implement strict rate limiting on the FastAPI backend, especially on resource-intensive endpoints (like training or AI Assistant chat), to prevent abuse.
- **File Scanning**: Introduce a lightweight malware/virus scanning step for uploaded files before they are processed by pandas, as CSVs can sometimes contain macro injection payloads.

## 5. Known Minor Constraints
- **Currency Stripping**: The current `clean_and_coerce_numeric_columns` logic works well for standard US currency. It may need localization support in the future to handle European formats (e.g., `1.000,50 €`).
- **Categorical Cardinality**: If a user uploads a dataset with a high-cardinality categorical feature (like user IDs or raw text), the one-hot encoding step during ML prep might explode the memory. Introduce a cardinality threshold to automatically drop or hash such columns.
