"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { api } from "../../lib/api";
import styles from "./page.module.css";

export default function HistoryPage() {
    const router = useRouter();
    const [loading, setLoading] = useState(true);
    const [history, setHistory] = useState([]);
    const [error, setError] = useState("");

    useEffect(() => {
        fetchHistory();
    }, []);

    const fetchHistory = async () => {
        try {
            const data = await api.getMenuHistory(10, 0);
            if (data && data.menus) {
                setHistory(data.menus);
            } else {
                // Mock data if backend isn't ready
                setHistory(getMockHistory());
            }
        } catch (err) {
            console.error(err);
            setHistory(getMockHistory());
        } finally {
            setLoading(false);
        }
    };

    const getDaySpan = (weekStartStr) => {
        const start = new Date(weekStartStr);
        const end = new Date(start);
        end.setDate(end.getDate() + 6);

        const startStr = start.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
        const endStr = end.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
        return `${startStr} — ${endStr}`;
    };

    if (loading) {
        return (
            <div className={styles.loadingContainer}>
                <div className="spinner"></div>
                <p>Loading your culinary history...</p>
            </div>
        );
    }

    return (
        <main className={styles.container}>
            <header className={styles.header}>
                <div>
                    <button className="btn btn-ghost" onClick={() => router.push("/calendar")} style={{ marginLeft: "-1rem", marginBottom: "0.5rem" }}>
                        ← Back to Current Week
                    </button>
                    <h1 className="section-title">Past Menus</h1>
                    <p className="section-subtitle">Browse your previous weekly guides.</p>
                </div>
            </header>

            {history.length === 0 ? (
                <div className={styles.emptyState}>
                    <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>📚</div>
                    <h3>No history yet</h3>
                    <p>Your past weekly menus will appear here.</p>
                </div>
            ) : (
                <div className={styles.grid}>
                    {history.map((menu, idx) => (
                        <div
                            key={menu.id}
                            className={`glass-card ${styles.historyCard}`}
                            style={{ animationDelay: `${idx * 0.1}s` }}
                        >
                            <div className={styles.cardHeader}>
                                <span className={styles.weekLabel}>Week of</span>
                                <h3 className={styles.dateRange}>{getDaySpan(menu.week_start)}</h3>
                            </div>

                            <div className={styles.stats}>
                                <div className={styles.stat}>
                                    <span className={styles.statLabel}>Status</span>
                                    <span className={styles.statValue}>{menu.status || "Completed"}</span>
                                </div>
                                {menu.total_weekly_calories && (
                                    <div className={styles.stat}>
                                        <span className={styles.statLabel}>Avg Calories</span>
                                        <span className={styles.statValue}>
                                            {Math.round(menu.total_weekly_calories / 7)} / day
                                        </span>
                                    </div>
                                )}
                            </div>

                            <button
                                className="btn btn-secondary w-full"
                                onClick={() => alert("Viewing detailed past menus coming soon!")}
                                style={{ width: "100%", marginTop: "1.5rem" }}
                            >
                                View Full Menu
                            </button>
                        </div>
                    ))}
                </div>
            )}
        </main>
    );
}

function getMockHistory() {
    const today = new Date();
    const generatePastWeek = (weeksAgo) => {
        const d = new Date(today);
        d.setDate(d.getDate() - d.getDay() - 1 - (weeksAgo * 7));
        return {
            id: `mock-hist-${weeksAgo}`,
            week_start: d.toISOString(),
            status: "completed",
            total_weekly_calories: 14200 + (Math.random() * 800)
        };
    };

    return [generatePastWeek(1), generatePastWeek(2), generatePastWeek(3)];
}
