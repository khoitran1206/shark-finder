# Shark Finder frontend

React + TypeScript + Vite + Tailwind. See the root [README](../README.md) for setup, configuration and Docker.

```bash
npm ci
npm run dev      # http://localhost:5173
npm run build
npm run lint
```

Auth uses AWS Amplify (Cognito). The pool IDs are hardcoded in `src/main.tsx`; `amplify_outputs.json` is imported by `src/amplify.ts` but is currently a stub.
