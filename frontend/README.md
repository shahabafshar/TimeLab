# TimeLab Frontend

Next.js React frontend for TimeLab time series forecasting platform.

## Quick Start

```bash
npm install
npm run dev
```

Open http://localhost:3000

## Environment Variables

Create `.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Project Structure

- `app/` - Next.js app router pages
- `src/components/` - React components
  - `charts/` - Visualization components
  - `models/` - Model training components
  - `evaluation/` - Evaluation components
  - `forecasting/` - Forecasting components
  - `workflow/` - Workflow wizard
  - `ui/` - UI primitives
- `src/lib/` - Utilities and API clients
- `src/types/` - TypeScript type definitions

## Build

```bash
npm run build
npm start
```
