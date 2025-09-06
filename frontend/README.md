# upGrad Clone - Frontend

A modern, responsive React-based website built with Next.js and Tailwind CSS that replicates the upGrad education platform design and functionality.

## ✨ Features

- **🎨 Authentic upGrad Design**: Faithful recreation of upGrad's visual identity and layout
- **📚 Course Showcase**: Display of popular programs including DBA, MBA, Data Science, and AI courses
- **🏫 University Partnerships**: Showcase of partner universities and institutions
- **🔍 Search Functionality**: Course search and exploration features
- **📱 Responsive Design**: Mobile-first design that works on all devices
- **🎯 Interactive Navigation**: Dropdown menus and smooth user interactions
- **📊 Statistics Display**: Key metrics and achievements section
- **💼 Professional Layout**: Clean, modern interface matching upGrad's brand

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Backend API running on http://localhost:8000

### Installation

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Set up environment variables:**
   ```bash
   cp env.example .env.local
   # Edit .env.local with your configuration
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

4. **Open your browser:**
   Navigate to [http://localhost:3000](http://localhost:3000)

## 🛠️ Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

### Project Structure

```
frontend/
├── src/
│   ├── app/                 # Next.js app directory
│   │   ├── globals.css      # Global styles
│   │   ├── layout.tsx       # Root layout
│   │   └── page.tsx         # Main dashboard page
│   ├── components/          # React components
│   │   ├── DashboardHeader.tsx
│   │   ├── MetricCard.tsx
│   │   ├── LearnerCard.tsx
│   │   ├── NudgeGenerator.tsx
│   │   ├── RiskChart.tsx
│   │   ├── FilterPanel.tsx
│   │   └── LoadingSpinner.tsx
│   ├── lib/                 # Utilities and API client
│   │   ├── api.ts           # API client
│   │   └── utils.ts         # Helper functions
│   └── types/               # TypeScript type definitions
│       └── index.ts
├── public/                  # Static assets
├── package.json
├── tailwind.config.js       # Tailwind configuration
├── tsconfig.json           # TypeScript configuration
└── next.config.js          # Next.js configuration
```

## 🎨 Design System

### Color Palette

- **Primary**: Blue gradient (#3B82F6 to #8B5CF6)
- **Success**: Green (#10B981)
- **Warning**: Yellow (#F59E0B)
- **Error**: Red (#EF4444)
- **Background**: Dark gradient (slate-900 to purple-900)

### Components

All components are built with:
- **Framer Motion** for smooth animations
- **Tailwind CSS** for styling
- **Radix UI** for accessible primitives
- **Lucide React** for icons

## 🔌 API Integration

The frontend connects to the backend API with the following endpoints:

- `GET /api/health` - Health check
- `GET /api/learners` - Get all learners
- `GET /api/learners?risk={level}` - Filter learners by risk
- `POST /api/learners/{id}/nudge` - Generate nudge for learner

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_BASE` | Backend API URL | `http://localhost:8000` |
| `NEXT_PUBLIC_DEBUG` | Enable debug mode | `false` |

## 🎯 Key Features

### Dashboard Overview
- Real-time metrics cards with animated counters
- Interactive risk distribution chart
- Learner cards with expandable details
- Quick action buttons

### Learner Management
- Visual risk indicators with color coding
- Completion percentage and quiz scores
- Contact information display
- Last login tracking

### Nudge Generation
- Multi-channel support (in-app, WhatsApp, email)
- AI-powered content generation
- Fallback mode indicators
- Copy-to-clipboard functionality

### Filtering & Actions
- Risk level filtering
- Bulk actions support
- Data export capabilities
- Real-time refresh

## 🚀 Deployment

### Build for Production

```bash
npm run build
npm run start
```

### Docker Deployment

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is part of the CodeRed Learner Engagement Platform.

## 🆘 Support

For support and questions:
- Check the backend API is running
- Verify environment variables are set correctly
- Check browser console for errors
- Ensure all dependencies are installed
