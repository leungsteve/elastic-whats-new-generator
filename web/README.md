# Elastic What's New Generator - Web UI

A modern, responsive web interface for the Elastic What's New Generator that allows users to dynamically manage features and generate presentations and lab workshops.

## Features

### 🎯 **Feature Management**
- **Dynamic Feature Creation**: Add new features with descriptions, benefits, and documentation links
- **Visual Feature Dashboard**: Browse and search features with domain-specific filtering
- **Real-time Search**: Instantly filter features by name, description, or domain
- **Domain Organization**: Filter by Search, Observability, Security, or All Domains

### 📊 **Presentation Generation**
- **Interactive Feature Selection**: Choose features for presentation generation
- **Multi-Domain Support**: Generate unified presentations or domain-specific content
- **Audience Targeting**: Business, Technical, or Mixed audience options
- **Live Preview**: See generated presentation content before export
- **Multiple Export Formats**: Standard Markdown, GitHub Flavored, Reveal.js

### 🧪 **Lab Workshop Creation**
- **Hands-on Lab Generation**: Create interactive workshops from features
- **Multiple Lab Formats**: Standard, GitHub, and Instruqt compatible
- **Workshop Management**: Combine multiple labs into comprehensive tracks
- **Export Options**: Inline viewing or downloadable files

### 📥 **Export Management**
- **Format Options**: Standard, GitHub, Reveal.js, Instruqt
- **Download Integration**: Direct file downloads via REST API
- **Export History**: Track previously generated content (coming soon)

## Getting Started

### Prerequisites
- FastAPI server running on `http://localhost:8000`
- Modern web browser with JavaScript enabled

### Access the UI
1. Start the FastAPI server:
   ```bash
   cd elastic-whats-new-generator
   source venv/bin/activate
   PYTHONPATH=. python src/api/main.py
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:8000
   ```

### Quick Start Guide

#### 1. Add Your First Feature
- Click **"Add Feature"** in the top right
- Fill in the feature details:
  - **Name**: e.g., "Advanced Search Filters"
  - **Description**: Brief description of the feature
  - **Domain**: Search, Observability, or Security
  - **Benefits**: One benefit per line
  - **Documentation Links**: URLs to relevant docs
- Click **"Save Feature"**

#### 2. Generate a Presentation
- Navigate to the **"Presentations"** tab
- Select features you want to include
- Choose domain, quarter, and audience
- Click **"Generate Presentation"**
- Preview the content and export in your preferred format

#### 3. Create Lab Workshops
- Go to the **"Labs"** tab
- Select features for hands-on exercises
- Set workshop title and format
- Click **"Generate Labs"**
- Export as inline content or downloadable files

## User Interface Overview

### Navigation
- **Features**: Manage your feature database
- **Presentations**: Generate business and technical presentations
- **Labs**: Create hands-on workshop content
- **Exports**: View and manage export history

### Domain Filtering
Filter content by Elastic domains:
- **Search**: Elasticsearch core search functionality
- **Observability**: Monitoring, logging, and APM features
- **Security**: SIEM, threat detection, and security analytics
- **All Domains**: Cross-platform unified content

### Export Formats

#### Presentations
- **Standard Markdown**: Clean, readable format
- **GitHub Flavored**: Enhanced with tables and task lists
- **Reveal.js**: Presentation framework compatible

#### Labs
- **Standard**: Basic markdown format
- **GitHub**: Enhanced with badges and emojis
- **Instruqt**: Platform-specific formatting for hands-on labs

## API Integration

The web UI integrates with the following REST API endpoints:

### Feature Management
- `POST /features` - Create new features
- `GET /features` - List all features (when available)
- `DELETE /features/{id}` - Delete features

### Presentation Generation
- `POST /presentations/complete` - Generate domain-specific presentations
- `POST /presentations/unified` - Generate cross-domain presentations
- `POST /presentations/markdown/export` - Export to downloadable files
- `POST /presentations/markdown/inline` - Get inline markdown content

### Lab Generation
- `POST /labs/markdown/single` - Generate single lab
- `POST /labs/markdown/export` - Generate multiple labs
- Support for inline and file export formats

## Browser Compatibility

Tested and supported on:
- Chrome 90+ ✅
- Firefox 88+ ✅
- Safari 14+ ✅
- Edge 90+ ✅

## Development

### File Structure
```
web/
├── index.html      # Main HTML structure
├── styles.css      # CSS styling and responsive design
├── app.js          # JavaScript application logic
└── README.md       # This documentation
```

### Customization
- **Styling**: Modify `styles.css` for visual customization
- **API Endpoint**: Update `apiBase` in `app.js` for different server locations
- **Features**: Extend functionality in the `ElasticGenerator` class

### Local Development
The UI uses vanilla HTML/CSS/JavaScript for simplicity:
- No build process required
- Direct file editing and refresh
- CORS enabled for local development

## Troubleshooting

### Common Issues

**UI Not Loading**
- Verify FastAPI server is running on port 8000
- Check browser console for JavaScript errors
- Ensure CORS is enabled in the API

**Features Not Displaying**
- The UI falls back to sample data if the API is unavailable
- Check network tab for API call failures
- Verify feature data format matches expected schema

**Export Not Working**
- Ensure selected features exist and are valid
- Check browser's download settings
- Verify API endpoints are responding correctly

### Getting Help
- Check browser developer console for errors
- Verify API health at `http://localhost:8000/health`
- Review network requests in browser dev tools

## Future Enhancements

Planned improvements include:
- **Real-time collaboration** for multi-user editing
- **Template customization** for presentations and labs
- **Export history management** with search and filtering
- **Batch operations** for bulk feature management
- **Advanced analytics** for content generation insights
- **Integration with external systems** (Confluence, GitHub, etc.)

---

For technical details about the backend API, see the main project documentation.