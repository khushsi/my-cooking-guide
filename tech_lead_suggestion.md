# Tech Lead Codebase Review & Suggestions

Here are the key technical problems, design flaws, and architecture issues found during the comprehensive codebase review. This should serve as the roadmap for technical debt reduction and refactoring.

## 1. Backend Architecture & Modularity
**Issue:** Business logic is firmly entangled with routing layers.
- `routers/auth.py`, `routers/menu.py`, and `routers/onboarding.py` all contain direct database execution logic (`db.execute(select(...))`).
- **Suggestion:** Adopt a layered architecture (Controller -> Service -> Repository). Create proper domain services (`user_service.py`, `menu_service.py`) that encapsulate business logic, leaving routers to handle only HTTP requests and responses.

## 2. Security & Vulnerabilities
**Issue:** Passwords are not hashed securely.
- `routers/auth.py` contains a custom `hash_password` function that merely uses `sha256` without salting, explicitly noted as "non-production hash". 
- **Suggestion:** Immediately replace the hashing logic with `passlib` and `bcrypt` for secure password storage.

## 3. Database Persistence & Bypasses
**Issue:** Bypassing standard repository patterns.
- Direct `db.add()` and `db.flush()` calls in routes make the codebase hard to mock for testing and tightly coupled to the ORM.
- While entities are persisted, any change to the DB schema requires updating every single route.
- **Suggestion:** Introduce a Data Access Layer (DAL) or Repository pattern to abstract database operations.

## 4. Over-reliance on AI & Error Handling
**Issue:** LLM responses govern primary application state.
- In `routers/menu.py`, the AI's JSON output for `generate_weekly_menu` is directly shoved into the `menu_data` field and assumed to be correctly formatted. If the AI hallucinates keys or types, the frontend will break.
- **Suggestion:** Always parse and strictly validate AI output through a Pydantic schema (e.g., `model_validate(json_data)`) before storing it. Fallback deterministic logic should be employed if the AI fails.

## 5. Frontend Architecture & Modularity
**Issue:** monolithic component files.
- Files like `calendar/page.js` (300+ lines) and `onboarding/page.js` (500+ lines) possess zero modularity. They handle multiple complex views (modals, calendars, cards, 4 onboarding steps) in one massive component.
- **Suggestion:** Break UI into smaller, reusable components (`<MealCard />`, `<SwapModal />`, `<StepDietType />`). This will improve readability, maintainability, and reusability.

## 6. Frontend State Management & Clean Code
**Issue:** "Prop drilling" risk and local state bloat.
- Extensive use of multiple `useState` hooks for complex state (e.g., handling 10+ variables in onboarding).
- Direct modification/reading of `localStorage` inside UI components (e.g., setting `demoPreferences`).
- **Suggestion:** Abstract API logic and global state. Use a state management tool (Zustand, Redux) or at least React Context for heavy flows like Onboarding. Move `localStorage` logic into a separate `storage` utility file.

---
**Summary Action Items for the Team:**
1. Refactor backend into Controller/Service/Repository layers.
2. Upgrade password hashing to `bcrypt`.
3. Add Pydantic validation over all AI-generated outputs.
4. Split frontend page files into modular directories with distinct components.
