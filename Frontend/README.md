# FoundrAI — Frontend

> From Idea to Startup, Powered by AI

The FoundrAI frontend is a React 19 + TanStack Start application that provides the full user interface for the FoundrAI AI startup creation platform.

---

## Tech Stack

| Technology | Version | Role |
|---|---|---|
| React | 19.x | UI library |
| TypeScript | 5.x | Language |
| TanStack Router | 1.x | File-based routing |
| TanStack Query | 5.x | Server state management |
| TanStack Start | 1.x | SSR framework |
| Vite | 8.x | Build tool |
| Tailwind CSS | 4.x | Styling |
| Radix UI | Latest | Accessible UI primitives |
| Framer Motion | 12.x | Animations |
| Recharts | 2.x | Charts |
| Zod | 3.x | Schema validation |
| React Hook Form | 7.x | Form management |

---

## Requirements

- **Node.js** >= 20.x ([install via nvm](https://github.com/nvm-sh/nvm#installing-and-updating))
- **npm** >= 9.x (comes with Node.js) — or use `bun`, `pnpm`, or `yarn`

---

## Getting Started

### 1. Clone the repository

```bash
git clone <repository-url>
cd FoundrAI/Frontend
```

### 2. Install dependencies

Choose any one package manager:

```bash
# npm (recommended for most users)
npm install

# bun (fastest)
bun install

# pnpm
pnpm install

# yarn
yarn install
```

All dependencies are listed in `package-requirements.txt` for reference.

### 3. Configure environment

Create a `.env.local` file in the `Frontend/` directory:

```bash
cp .env.example .env.local   # if .env.example exists
```

Or create it manually:

```env
VITE_API_URL=http://localhost:8000
```

> If you are running the frontend standalone (no backend), you can skip this step.

### 4. Start the development server

```bash
npm run dev
```

The app will start at **http://localhost:8080** (or the next available port if 8080 is in use).

---

## Available Scripts

| Script | Command | Description |
|---|---|---|
| Development server | `npm run dev` | Start Vite dev server with HMR |
| Production build | `npm run build` | Build optimised production output |
| Dev build | `npm run build:dev` | Build with development mode flags |
| Preview build | `npm run preview` | Serve the production build locally |
| Lint | `npm run lint` | Run ESLint across all source files |
| Format | `npm run format` | Run Prettier and write changes |

---

## Project Structure

```
Frontend/
├── src/
│   ├── routes/          # TanStack Router file-based routes
│   ├── components/      # Reusable UI components
│   │   └── ui/          # shadcn/ui base components
│   ├── hooks/           # Custom React hooks
│   ├── lib/             # Utilities, API client, helpers
│   ├── assets/          # Static assets (images, fonts)
│   ├── styles.css       # Global styles + Tailwind base
│   ├── router.tsx       # Router configuration
│   ├── start.ts         # TanStack Start entry point
│   └── server.ts        # SSR server entry (Nitro)
├── package.json         # Project manifest and scripts
├── package-requirements.txt  # Human-readable dependency list
├── vite.config.ts       # Vite configuration
├── tsconfig.json        # TypeScript configuration
└── README.md            # This file
```

---

## Dependency Reference

See [`package-requirements.txt`](./package-requirements.txt) for a categorised, annotated list of every dependency and its purpose. This file is the human-readable equivalent of a Python `requirements.txt`.

To install all dependencies from scratch:

```bash
npm install
```

npm resolves exact versions from `package.json` (ranges like `^1.2.0`) and locks them in `package-lock.json`. Use `bun install` if you prefer the `bun.lock` lockfile.

---

## Troubleshooting

**Port already in use**
Vite will automatically try the next available port. Check the terminal output for the actual URL.

**Module not found errors after clone**
Dependencies were not installed. Run `npm install` first.

**TypeScript errors on startup**
Run `npm run build` to see all type errors. The dev server will still run but may show warnings.

**Blank page in browser**
Check the browser console for errors. Most commonly caused by a missing `VITE_API_URL` environment variable when a backend call fires on mount.

---

## Notes

- This is the frontend only. The FoundrAI backend (FastAPI + Python) is a separate service. See the project documentation in `/docs` for the full system architecture.
- The app uses TanStack Start with Vite.

