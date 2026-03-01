"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "../../lib/api";
import styles from "./page.module.css";

export default function LoginPage() {
    const router = useRouter();
    const [isLogin, setIsLogin] = useState(true);
    const [name, setName] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError("");

        try {
            if (isLogin) {
                const data = await api.login({ email, password });
                localStorage.setItem("token", data.access_token);
            } else {
                const data = await api.signup({ name, email, password });
                localStorage.setItem("token", data.access_token);
            }

            // On success, redirect to onboarding personas
            router.push("/onboarding");
        } catch (err) {
            setError(err.message || "Authentication failed. Please check your credentials.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <main className={styles.container}>
            <div className={styles.authCard}>
                <h1 className={styles.title}>{isLogin ? "Welcome Back" : "Create Account"}</h1>
                <p className={styles.subtitle}>
                    {isLogin
                        ? "Log in to access your culinary guide."
                        : "Join to get AI-powered meal plans."}
                </p>

                {error && <div className={styles.errorBanner}>{error}</div>}

                <form onSubmit={handleSubmit} className={styles.form}>
                    {!isLogin && (
                        <div className={styles.inputGroup}>
                            <label htmlFor="name">Name</label>
                            <input
                                id="name"
                                type="text"
                                className="input"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                required={!isLogin}
                            />
                        </div>
                    )}

                    <div className={styles.inputGroup}>
                        <label htmlFor="email">Email Address</label>
                        <input
                            id="email"
                            type="email"
                            className="input"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />
                    </div>

                    <div className={styles.inputGroup}>
                        <label htmlFor="password">Password</label>
                        <input
                            id="password"
                            type="password"
                            className="input"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                    </div>

                    <button
                        type="submit"
                        className={`btn btn-primary ${styles.submitBtn}`}
                        disabled={loading || !email || !password || (!isLogin && !name)}
                    >
                        {loading ? <div className="spinner"></div> : (isLogin ? "Log In" : "Sign Up")}
                    </button>

                    <button
                        type="button"
                        className="btn btn-ghost"
                        onClick={() => {
                            setIsLogin(!isLogin);
                            setError("");
                        }}
                        style={{ marginTop: "1rem" }}
                    >
                        {isLogin ? "Need an account? Sign up" : "Already have an account? Log in"}
                    </button>
                </form>
            </div>
        </main>
    );
}
