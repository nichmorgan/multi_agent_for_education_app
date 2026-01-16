# Multi-Agent for Education App

A Django-based application leveraging multi-agent systems and graph databases for educational content analysis and interaction. This project uses Neo4j for knowledge graph storage, Google Gemini for AI capabilities, and Tesseract OCR for document processing.

## Prerequisites

Before you begin, ensure you have the following installed:

*   **Python**: Version 3.13 or higher.
*   **Neo4j Database**: Community or Enterprise edition (version 5.x recommended).
*   **Tesseract OCR**: A system-level dependency required for document parsing.
    *   **Windows/Linux/Mac**: Please refer to the [official installation guide](https://tesseract-ocr.github.io/tessdoc/Installation.html) for your operating system.
*   **uv**: Recommended for fast Python dependency management.
    *   Install via: `curl -LsSf https://astral.sh/uv/install.sh | sh` (or see [docs](https://github.com/astral-sh/uv)).

## Installation

1.  **Clone the Repository**

    ```bash
    git clone <repository_url>
    cd multi_agent_for_education_app
    ```

2.  **Environment Setup**

    Create a `.env` file in the root directory. You can copy the structure below:

    ```ini
    # .env
    GOOGLE_API_KEY=your_google_gemini_api_key
    
    # Neo4j Configuration
    NEO4J_URI=bolt://localhost:7687
    NEO4J_USERNAME=neo4j
    NEO4J_PASSWORD=your_neo4j_password
    ```

3.  **Install Dependencies**

    Using `uv` (recommended):
    ```bash
    uv sync
    ```

    Or using standard pip:
    ```bash
    pip install -r requirements.txt
    ```

## Database Setup

1.  **Apply Migrations**
    
    Initialize the SQLite database for Django and Huey:
    ```bash
    python manage.py migrate
    ```

2.  **Verify Neo4j Connection**

    Ensure your Neo4j instance is running, then verify the connection configuration:
    ```bash
    python verify_neo4j.py
    ```

## Running the Application

You need to run two processes: the Django development server and the Huey task consumer.

1.  **Start Django Server**
    
    ```bash
    python manage.py runserver
    ```
    Access the app at `http://localhost:8000`.

2.  **Start Huey Task Consumer**
    
    Run this in a separate terminal to handle background tasks (like file ingestion):
    ```bash
    python manage.py djangohuey
    ```
