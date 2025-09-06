# Learner Engagement Platform Dashboard

A Streamlit-based administrative interface for monitoring learner risk levels and generating personalized interventions.

## Features

- **Learner Overview**: View all learners with risk scores and completion metrics
- **Risk Filtering**: Filter learners by risk level (low, medium, high)
- **Manual Nudge Generation**: Generate personalized nudges for individual learners
- **Fallback Indicators**: Clear visual indicators when AI services are unavailable
- **Real-time Metrics**: Summary statistics and color-coded risk levels

## Setup Instructions

### Prerequisites
- Python 3.8+
- Backend API running on http://localhost:8000 (or configured API_BASE)

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the dashboard:
```bash
streamlit run app.py
```

3. Open your browser to http://localhost:8501

### Configuration

Set the `API_BASE` environment variable to point to your backend API:

```bash
# Windows
set API_BASE=http://localhost:8000

# Linux/Mac
export API_BASE=http://localhost:8000
```

## Usage

1. **Monitor Learners**: View the learner table with risk scores and completion rates
2. **Filter by Risk**: Use the sidebar filter to focus on specific risk levels
3. **Generate Nudges**: 
   - Expand a learner's section
   - Select the communication channel (in-app, WhatsApp, email)
   - Click "Generate Nudge" to create personalized content
4. **Review Results**: Generated nudges show fallback status and content details

## Error Handling

The dashboard includes comprehensive error handling for:
- Backend API connectivity issues
- Request timeouts
- Invalid responses
- Missing data

Error messages provide clear guidance for troubleshooting common issues.

## Development

The dashboard is built with:
- **Streamlit**: Web interface framework
- **Requests**: HTTP client for API communication
- **Pandas**: Data manipulation and display