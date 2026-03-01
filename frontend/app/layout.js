import "./globals.css";

export const metadata = {
  title: "My Cooking Guide — AI Meal Planner",
  description:
    "A smart, AI-powered weekly meal planner that generates nutritionally balanced menus based on your ingredients, energy levels, and dietary needs.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta name="theme-color" content="#0a0e1a" />
      </head>
      <body>{children}</body>
    </html>
  );
}
