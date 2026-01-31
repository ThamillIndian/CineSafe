# 🎬 CineSafe Frontend

Beautiful, responsive React interface for the Film Production Analyzer.

## 🚀 Quick Start

### Prerequisites
- Node.js 16+ 
- npm or yarn

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

The app will be available at `http://localhost:3000`

### Build for Production

```bash
npm run build
npm run preview
```

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable React components
│   │   ├── Sidebar.jsx      # Animated navigation sidebar
│   │   ├── ProgressOverlay.jsx  # Analysis progress animation
│   │   └── ExportButton.jsx     # Export data button
│   ├── pages/               # Page components
│   │   ├── Home.jsx         # Upload & analysis page
│   │   ├── Analysis.jsx     # Analysis results with tabs
│   │   ├── ExecutiveReport.jsx  # Executive summary
│   │   └── DetailedSceneView.jsx # Scene details modal
│   ├── hooks/               # Custom React hooks
│   │   └── useAnalysisData.js   # Data management hook
│   ├── services/            # API service layer
│   │   └── api.js           # Backend API calls
│   ├── styles/              # CSS stylesheets
│   │   ├── globals.css      # Global styles
│   │   ├── sidebar.css      # Sidebar animations
│   │   └── components.css   # Component styles
│   ├── App.jsx              # Main app component
│   ├── App.css
│   └── index.js             # Entry point
├── public/
│   └── index.html
├── package.json
├── vite.config.js           # Vite configuration
└── README.md
```

## 🎨 Features

### Pages
1. **Home Page** 
   - Drag & drop file upload
   - Animated progress overlay during analysis
   - Auto-navigate to results when complete

2. **Analysis Page**
   - 6 tabs for different analysis views
   - Scene extraction results
   - Risk intelligence visualization
   - Budget breakdown
   - Location optimization clusters
   - Schedule optimization timeline
   - Department scaling analysis

3. **Executive Report**
   - KPI cards with key metrics
   - Budget optimization summary
   - Schedule compression details
   - Actionable recommendations
   - Export to JSON

4. **Detailed Scene View**
   - Modal popup for individual scenes
   - Complete risk & budget data
   - Location clustering info
   - Mitigation recommendations

### UI Components
- **Sidebar**: Animated navigation that expands on hover, pages locked until data loads
- **Progress Overlay**: Real-time analysis progress with visual timeline
- **Data Tables**: Sortable, responsive tables with rich formatting
- **Cards**: Beautiful gradient cards with hover effects
- **Charts**: Grid-based dashboard layouts

### Animations
- Smooth page transitions
- Hover effects on interactive elements
- Loading spinners and progress indicators
- Slide and fade animations

## 🔌 API Integration

The frontend connects to the backend API at `http://localhost:8000/api/v1`

### Key Endpoints Used:
- `POST /scripts/upload` - Upload script file
- `POST /runs/{documentId}/start` - Start analysis
- `GET /runs/{runId}/result` - Fetch analysis results

## 📱 Responsive Design

- Desktop: Full layout with all features
- Tablet: Adjusted grid layouts
- Mobile: Single column, optimized for touch

## 🛠️ Tech Stack

- **React 18** - UI framework
- **Vite** - Build tool & dev server
- **CSS3** - Styling with animations
- **Axios** - HTTP client (optional, using fetch)

## 🚀 Deployment

### Development
```bash
npm run dev
```

### Production Build
```bash
npm run build
npm run preview
```

Output files go to `dist/` folder

### Docker (Optional)
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "run", "preview"]
```

## 📝 Environment Variables

Create a `.env` file in the root:

```
VITE_API_URL=http://localhost:8000/api/v1
```

## 🎯 Key Features

✅ **Dynamic Navigation** - Pages unlock when analysis completes
✅ **Real-time Progress** - Live updates during analysis
✅ **Beautiful UI** - Gradient backgrounds, smooth animations
✅ **Responsive Design** - Works on all screen sizes
✅ **Data Visualization** - Tables, cards, and grids
✅ **Export Functionality** - Download analysis as JSON
✅ **Modal Popups** - Detailed scene information
✅ **Color-coded Risks** - Visual risk indicators

## 🐛 Troubleshooting

### Port 3000 already in use?
```bash
npm run dev -- --port 3001
```

### API not connecting?
- Ensure backend is running on `http://localhost:8000`
- Check VITE_API_URL in environment variables
- Check browser console for CORS errors

### Styles not loading?
- Clear browser cache (Ctrl+Shift+Delete)
- Run `npm run dev` again

## 📞 Support

For issues or questions, check:
- Backend logs: `backend/QWEN3_QUICK_START.md`
- API documentation: Backend Swagger UI at `http://localhost:8000/docs`

---

**Built with ❤️ for CineSafe Film Production Analyzer** 🎬🏴‍☠️
