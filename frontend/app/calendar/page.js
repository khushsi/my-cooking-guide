"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { api } from "../../lib/api";
import { storage } from "../../lib/storage";
import styles from "./page.module.css";

import MealCard from "../../components/Calendar/MealCard";
import SwapModal from "../../components/Calendar/SwapModal";

export default function CalendarPage() {
    const router = useRouter();
    const [menu, setMenu] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    // Modal state
    const [isModalOpen, setModalOpen] = useState(false);
    const [activeSwap, setActiveSwap] = useState(null); // { dayIndex, mealType, meal }
    const [swapLoading, setSwapLoading] = useState(false);

    useEffect(() => {
        const token = storage.get("token");
        if (!token) {
            router.push("/login"); // Fixed path
            return;
        }

        const fetchMenu = async () => {
            try {
                // Try getting the current active menu
                let res = await api.getCurrentMenu();

                if (!res || !res.menu_data) { // Adjusted check based on backend response schema
                    // Try generating if none exists (only if not a demo token)
                    if (!token.startsWith("demo-token")) {
                        res = await api.generateMenu();
                    }
                }

                if (res && res.menu_data) {
                    setMenu({
                        ...res,
                        days: res.menu_data // Map backend field to expected frontend name
                    });
                } else {
                    // Fallback to demo data
                    const demo = storage.get("demoMenu");
                    if (demo) setMenu(demo);
                }
            } catch (err) {
                console.error("Failed to fetch menu", err);
                setError("Could not load your menu. Please check your connection or API key.");
            } finally {
                setLoading(false);
            }
        };

        fetchMenu();
    }, [router]);

    const handleSwapRequest = (type, meal, dayIndex) => {
        setActiveSwap({ dayIndex, mealType: type, meal });
        setModalOpen(true);
    };

    const handleConfirmSwap = async (reason) => {
        setSwapLoading(true);
        try {
            const dayData = menu.days[activeSwap.dayIndex];
            const menuId = menu.id || "current";

            const res = await api.swapMeal(menuId, {
                day_index: activeSwap.dayIndex,
                meal_type: activeSwap.mealType,
                reason
            });

            if (res && res.menu_data) {
                setMenu({
                    ...res,
                    days: res.menu_data
                });
                setModalOpen(false);
                setActiveSwap(null);
            }
        } catch (err) {
            console.error("Swap failed", err);
            alert("Failed to swap meal. Please try again.");
        } finally {
            setSwapLoading(false);
        }
    };

    if (loading) {
        return (
            <div className={styles.loaderContainer}>
                <div className="spinner" style={{ width: 50, height: 50 }} />
                <p>Tailoring your culinary week...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className={styles.errorContainer}>
                <h1>Oops!</h1>
                <p>{error}</p>
                <button className="btn btn-primary" onClick={() => window.location.reload()}>
                    Retry
                </button>
            </div>
        )
    }

    if (!menu) {
        return (
            <div className={styles.errorContainer}>
                <h1>No menu found</h1>
                <button className="btn btn-primary" onClick={() => router.push("/onboarding")}>
                    Start Onboarding
                </button>
            </div>
        );
    }

    return (
        <main className={styles.container}>
            <header className={styles.header}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
                    <h1 className="section-title">Your Weekly Plan</h1>
                    <nav style={{ display: 'flex', gap: '15px' }}>
                        <button className="btn-link" onClick={() => router.push("/pantry")}>Pantry</button>
                        <button className="btn-link" onClick={() => router.push("/grocery-list")} style={{ color: 'var(--accent)' }}>Grocery List</button>
                    </nav>
                </div>
                <div className={styles.statsBar}>
                    <button
                        className="btn btn-primary"
                        style={{ marginRight: '20px', padding: '8px 16px', fontSize: '0.9rem' }}
                        onClick={() => router.push("/grocery-list")}
                    >
                        View Shopping List
                    </button>
                    <div className={styles.stat}>
                        <span className={styles.statLabel}>Avg Daily Cal</span>
                        <span className={styles.statValue}>{menu.days ? Math.round(menu.total_weekly_calories / 7) || 2000 : 2000}</span>
                    </div>
                    <div className={styles.stat}>
                        <span className={styles.statLabel}>Est. Cost</span>
                        <span className={styles.statValue}>${menu.total_weekly_cost_estimate || 85}</span>
                    </div>
                </div>
            </header>

            <div className={styles.calendarGrid}>
                {menu.days && menu.days.map((day, idx) => (
                    <div key={day.date || idx} className={styles.dayColumn}>
                        <div className={styles.dayHeader}>
                            <h3>{day.day}</h3>
                            <span suppressHydrationWarning>
                                {day.date ? new Date(day.date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }) : ""}
                            </span>
                        </div>

                        <div className={styles.mealsList}>
                            {day.meals && Object.entries(day.meals).map(([type, meal]) => (
                                <MealCard
                                    key={type}
                                    type={type}
                                    meal={meal}
                                    onSwap={(t, m) => handleSwapRequest(t, m, idx)}
                                    aria-label={`Swap ${type} for ${day.day}`}
                                />
                            ))}
                        </div>
                    </div>
                ))}
            </div>

            <section className={styles.prepSection}>
                <h2 className="section-title" style={{ fontSize: "1.2rem" }}>🔥 Prep Strategy</h2>
                <div className={styles.prepGrid}>
                    {menu.prep_plan?.map((step, i) => (
                        <div key={i} className={`glass-card ${styles.prepItem}`}>
                            <span className={styles.prepTime}>{step.estimated_time_minutes}m</span>
                            <p>{step.action}</p>
                            <div className={styles.prepFor}>for {step.for_meals?.join(", ")}</div>
                        </div>
                    ))}
                    {(!menu.prep_plan || menu.prep_plan.length === 0) && (
                        <p style={{ color: "var(--text-dim)" }}>No batch prep steps for this week.</p>
                    )}
                </div>
            </section>

            <SwapModal
                isOpen={isModalOpen}
                meal={activeSwap?.meal}
                loading={swapLoading}
                onClose={() => setModalOpen(false)}
                onConfirm={handleConfirmSwap}
            />
        </main>
    );
}
