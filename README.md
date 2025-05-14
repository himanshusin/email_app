# EmailFlow Pro

**EmailFlow Pro** is an enterprise email management and analytics dashboard built with Streamlit. It provides real-time monitoring, categorization, and AI-powered reply generation for incoming emails, making it ideal for support and operations teams.

## Features

- 📧 **Dashboard Overview**: Visualize total, high-priority, processed, and pending emails.
- 📊 **Analytics**: Interactive charts for issue category distribution and email volume trends.
- 🏷️ **AI Categorization**: Automatically categorize emails into business-relevant categories.
- 🤖 **AI Reply Drafting**: Instantly generate professional replies for incoming emails.
- 📨 **Recent Emails**: Tabbed views for all, high-priority, and processed emails.
- ⚙️ **Configurable Settings**: Adjust refresh intervals and AI automation from the sidebar.

## Quick Start

1. **Clone the repository** and navigate to the project folder:
   ```bash
   git clone <your-repo-url>
   cd email_app
   ```
2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install dependencies:**
   ```bash
   pip install streamlit pandas numpy plotly transformers openai
   ```
4. **Run the app:**
   ```bash
   streamlit run app1.py
   ```

## Dependencies
- streamlit
- pandas
- numpy
- plotly
- transformers
- openai

## Notes
- The current version uses mock email data and AI functions for demonstration.
- For production, connect to real email servers and integrate actual AI models.

## Screenshots
![Dashboard Screenshot](screenshot.png)

## License
MIT
