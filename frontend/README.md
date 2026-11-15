# Shark Finder frontend

React + TypeScript + Vite + Tailwind. See the root [README](../README.md) for setup, configuration and Docker.

```bash
npm ci
npm run dev      # http://localhost:5173
npm run build
npm run lint
```

Auth uses AWS Amplify (Cognito). The pool and client IDs come from `VITE_COGNITO_*` (see `.env.example`), falling back to the current pool.

## Layout (`src/`)

```
main.tsx          app entry: Amplify config + router
config/           route URLs
routers/          Public/Investor/Firm route guards
pages/            one folder per role: General, Investor, Firm
components/       Auth, Navbar, MatchList (+ two thin wrappers), InvestorProfileForm,
                  PreviewDialog, LoadingScreen, form/ (TextField, SelectField), ui/ (shadcn)
hooks/            useProfileExists
services/         api-client (axios + Cognito token + request aborting)
lib/              apiError, investorPayload, text, utils
assets/           logos and video (imported, so they are bundled)
```
