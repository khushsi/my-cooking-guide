"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import styles from "./page.module.css";

export default function Home() {
  const router = useRouter();
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    setLoaded(true);
    // Check if user is already logged in
    const token = localStorage.getItem("token");
    if (token) {
      router.push("/calendar");
    }
  }, [router]);

  return (
    <main className={styles.hero}>
      {/* Animated background orbs */}
      <div className={styles.orbContainer}>
        <div className={`${styles.orb} ${styles.orb1}`} />
        <div className={`${styles.orb} ${styles.orb2}`} />
        <div className={`${styles.orb} ${styles.orb3}`} />
      </div>

      <div className={`${styles.content} ${loaded ? styles.visible : ""}`}>
        <div className={styles.badge}>
          <span className={styles.badgeDot} />
          AI-Powered Meal Planning
        </div>

        <h1 className={styles.title}>
          My Cooking
          <span className={styles.titleAccent}> Guide</span>
        </h1>

        <p className={styles.subtitle}>
          Generate nutritionally balanced weekly menus tailored to your
          ingredients, energy levels, and dietary needs. Powered by Google
          Gemini AI.
        </p>

        <div className={styles.features}>
          <div className={styles.feature}>
            <span className={styles.featureIcon}>📅</span>
            <span>Saturday-to-Saturday planning</span>
          </div>
          <div className={styles.feature}>
            <span className={styles.featureIcon}>🧠</span>
            <span>AI learns your taste</span>
          </div>
          <div className={styles.feature}>
            <span className={styles.featureIcon}>⚡</span>
            <span>Energy-aware recipes</span>
          </div>
        </div>

        <button
          className={`btn btn-primary btn-lg ${styles.ctaButton}`}
          onClick={() => router.push("/login")}
          id="get-started-btn"
        >
          Get Started — It&apos;s Free
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M5 12h14M12 5l7 7-7 7" />
          </svg>
        </button>

        <p className={styles.loginLink}>
          Already have an account?{" "}
          <a href="/login" className={styles.link}>
            Log in here
          </a>
        </p>
      </div>
    </main>
  );
}
