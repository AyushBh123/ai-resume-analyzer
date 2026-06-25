# AI Resume Analyzer - Frontend

Modern, responsive React + TypeScript frontend for the AI Resume Analyzer.

## 🚀 Features

- **Drag & Drop Upload**: Intuitive file upload with visual feedback
- **Real-time Analysis**: Live progress indicators during AI processing
- **Interactive Results**: Expandable sections, charts, and visualizations
- **Multi-Provider Support**: Switch between OpenAI, Anthropic, and Ollama
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- **Type-Safe**: Full TypeScript coverage for reliability
- **Modern UI**: Clean, professional design with Tailwind CSS

## 🛠️ Tech Stack

- **React 19** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first styling
- **Recharts** - Data visualization
- **React Dropzone** - File upload
- **Axios** - HTTP client
- **Lucide React** - Icon library

## 📦 Installation

```bash
# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Start development server
npm run dev
```

## 🔧 Configuration

Edit `.env` file:

```env
VITE_API_BASE_URL=http://localhost:8000
```

## 🏃 Running

### Development Mode

```bash
npm run dev
```

Access at: http://localhost:5173

### Production Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── FileUpload.tsx   # Drag-and-drop upload
│   │   ├── ScoreCard.tsx    # Score visualization
│   │   ├── SuggestionsList.tsx  # Improvement suggestions
│   │   └── AnalysisResults.tsx  # Complete results display
│   ├── services/            # API communication
│   │   └── api.ts           # Backend API client
│   ├── types/               # TypeScript definitions
│   │   └── api.ts           # API type definitions
│   ├── App.tsx              # Main application component
│   ├── main.tsx             # Application entry point
│   └── index.css            # Global styles
├── public/                  # Static assets
├── package.json             # Dependencies
├── vite.config.ts           # Vite configuration
├── tailwind.config.js       # Tailwind CSS config
└── tsconfig.json            # TypeScript config
```

## 🎨 Components

### FileUpload
Drag-and-drop file upload with validation:
- Accepts PDF and DOCX files
- Max file size: 10MB
- Visual feedback for drag state
- Error handling

### ScoreCard
Displays resume scores with visualizations:
- Radial chart for overall score
- Progress bars for breakdown
- Color-coded indicators
- Score interpretation

### SuggestionsList
Shows improvement suggestions:
- Grouped by priority (high/medium/low)
- Expandable details
- Category badges
- Impact descriptions

### AnalysisResults
Complete analysis display:
- Score cards
- Strengths and weaknesses
- Keywords analysis
- ATS compatibility
- Job match (if provided)
- Suggestions list

## 🔌 API Integration

The frontend communicates with the backend via REST API:

```typescript
// Upload and analyze
const result = await uploadAndAnalyze(file, jobDescription, provider);

// Check health
const health = await checkHealth();

// Analyze text directly
const result = await analyzeText(resumeText, jobDescription, provider);
```

## 🎯 Key Features Implementation

### File Upload
- Uses `react-dropzone` for drag-and-drop
- Validates file type and size
- Shows upload progress
- Handles errors gracefully

### Analysis Flow
1. User uploads resume file
2. Optional: Add job description
3. Select AI provider
4. Click "Analyze Resume"
5. Show loading state
6. Display comprehensive results

### Results Display
- Score visualization with Recharts
- Expandable suggestion cards
- Color-coded priority indicators
- Responsive grid layout
- Print-friendly styles

## 🎨 Styling

Uses Tailwind CSS for styling:
- Utility-first approach
- Responsive design
- Custom color palette
- Smooth animations
- Dark mode ready (future)

## 🔒 Type Safety

Full TypeScript coverage:
- API response types
- Component props
- State management
- Event handlers
- Service methods

## 📱 Responsive Design

Breakpoints:
- Mobile: < 640px
- Tablet: 640px - 1024px
- Desktop: > 1024px

## 🚀 Performance

Optimizations:
- Code splitting
- Lazy loading
- Memoization
- Efficient re-renders
- Optimized bundle size

## 🧪 Testing (Future)

```bash
# Run tests
npm test

# Run tests with coverage
npm run test:coverage
```

## 📝 Development Guidelines

### Code Style
- Use functional components
- Prefer hooks over classes
- Keep components small and focused
- Use TypeScript strictly
- Follow naming conventions

### Component Structure
```typescript
// 1. Imports
import React from 'react';
import { Icon } from 'lucide-react';

// 2. Types
interface Props {
  // ...
}

// 3. Component
const Component: React.FC<Props> = ({ prop }) => {
  // 4. State and hooks
  const [state, setState] = useState();

  // 5. Handlers
  const handleClick = () => {};

  // 6. Render
  return <div>...</div>;
};

// 7. Export
export default Component;
```

## 🐛 Troubleshooting

### Backend Connection Issues
```bash
# Check if backend is running
curl http://localhost:8000/health

# Verify VITE_API_BASE_URL in .env
```

### Build Errors
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Vite cache
rm -rf node_modules/.vite
```

### TypeScript Errors
```bash
# Check TypeScript configuration
npx tsc --noEmit

# Update types
npm install --save-dev @types/react @types/react-dom
```

## 📚 Resources

- [React Documentation](https://react.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Vite Guide](https://vitejs.dev/guide/)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [Recharts Documentation](https://recharts.org/)

## 🤝 Contributing

1. Follow the code style
2. Add TypeScript types
3. Test thoroughly
4. Update documentation
5. Submit pull request

## 📄 License

MIT License - see LICENSE file for details
