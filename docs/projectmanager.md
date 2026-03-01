# Project Manager Exploration Report: My Cooking Guide

**Date**: February 27, 2026
**Role:** Project Manager / Curious User
**Objective:** Explore the application, document user flows, identify logical failures, and outline must-have features to make the app stand out.

---

## 1. Flows Tested

During the exploration, the following user journeys were tested to evaluate the application's core functionality and user experience:

- **Account Registration & Login**: Successfully created two test accounts (`testpm1` and `testpm2`) and tested the authentication flow.
- **Onboarding Journey**: Proceeded through the initial onboarding steps, including persona selection ("Fitness Fanatic" for account 1, "Indian in USA" for account 2).
- **Core App Navigation**: Attempted to access main features including the Meal Planner (`/calendar`), "Grocery List", and "History".
- **Advanced Navigation**: Probed for expected standard routes such as `/settings`, `/search`, and `/dashboard` to see how the app handles edge cases and navigation.

---

## 2. Logical Failures and UX Friction Points

While acting as a curious user pushing the application's limits, several critical logical failures and UX issues were uncovered:

### Critical Blockers
* **Broken Onboarding (CORS Error)**: The onboarding process completely halts at the persona selection step. Clicking "Next" fails to advance the user due to a CORS policy error (`http://localhost:8000/api/menu/generate` is blocked). This prevents new users from actually experiencing the app.
* **Silent Failures**: The application lacks global error handling. When backend calls fail (e.g., during onboarding or when attempting to swap a meal), the UI provides absolutely zero feedback. The screen remains static, which is incredibly confusing for a user.

### Navigation and Routing
* **Missing Core Routes (404s)**: Expected routes like `/settings`, `/search`, and `/dashboard` return 404 Not Found errors, indicating incomplete feature scaffolding.
* **Unresponsive UI Elements**: Secondary actions like the "Grocery List" and "Swap" buttons on the calendar page are currently unresponsive.

### Authentication UX
* **Missing Logout**: There is no visible or accessible "Logout" button, trapping the user in their current session.
* **Session Redirection**: The login page does not automatically redirect already-authenticated users to their dashboard.
* **No Account Recovery**: The login page lacks a "Forgot Password" flow, which is a critical necessity for any live application.
* **Form Feedback**: The "Sign up" button is visually inconsistent and sometimes requires multiple clicks or precise targeting to trigger, and there is no real-time validation for signup inputs.

---

## 3. "Must-Have" Features for Launch

To ensure the application is usable and stands out, the following features are absolutely essential:

1. **Global Error Notifications (Toast/Banners)**: Users must be informed when something goes wrong (e.g., "Unable to generate menu, please check your connection or try again").
2. **Account Management Suite**: 
   - A functional "Profile Settings" page to manage dietary preferences, update passwords, and manage household personas.
   - A reliable "Forgot Password" flow via email.
3. **Empty States & Onboarding Tooltips**: The dashboard and calendar need meaningful empty states to guide users through creating their first meal plan when no data exists.
4. **Robust Search & Filtering**: A search feature for discovering recipes and ingredients is essential for long-term utility.
5. **Explicit Dietary Settings**: Beyond the initial persona templates, users need explicit toggles for hard restrictions (e.g., Allergies, Keto, Vegan, Gluten-Free).

---

## 4. PM Suggestions for Competitive Advantage

To elevate "My Cooking Guide" from a standard meal planner to a standout product, consider prioritizing these advanced features on the roadmap:

* **AI-Powered Pantry Substitutions**: Allow users to input what they currently have in their fridge, and use AI to suggest alternative ingredients for a recipe to reduce grocery trips.
* **Grocery Delivery Integration**: Implement a "one-click add-to-cart" feature that syncs the generated grocery list directly with services like Instacart or Amazon Fresh.
* **Multi-User Household Collaboration**: Allow family members or roommates to share a meal plan, add items to a shared grocery list, and vote on upcoming meals.
* **Gamified Consistency Tracking**: Introduce streaks or rewards for users who stick to their dietary goals or consistently log their home-cooked meals.
