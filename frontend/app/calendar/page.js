"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { api } from "../../lib/api";
import { storage } from "../../lib/storage";
import styles from "./page.module.css";

import MealCard from "../../components/Calendar/MealCard";
import SwapModal from "../../components/Calendar/SwapModal";
import IngredientSwapModal from "../../components/Calendar/IngredientSwapModal";
import MacroBoostModal from "../../components/Calendar/MacroBoostModal";
import NutritionSpotlight from "../../components/Calendar/NutritionSpotlight";

export default function CalendarPage() {
    const router = useRouter();
    const [menu, setMenu] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    // Modal state
    const [isModalOpen, setModalOpen] = useState(false);
    const [activeSwap, setActiveSwap] = useState(null); // { dayIndex, mealType, meal }
    const [swapLoading, setSwapLoading] = useState(false);

    const [isIngredientModalOpen, setIngredientModalOpen] = useState(false);
    const [activeIngredientSwap, setActiveIngredientSwap] = useState(null); // { dayIndex, mealType, ingredientName }
    const [ingredientOptions, setIngredientOptions] = useState([]);

    const [isBoostModalOpen, setBoostModalOpen] = useState(false);
    const [activeBoost, setActiveBoost] = useState(null); // { dayIndex, mealType, targetMacro }
    const [boostOptions, setBoostOptions] = useState([]);

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

    const handleIngredientSwapRequest = async (type, meal, dayIndex, ingredientName) => {
        setActiveIngredientSwap({ dayIndex, mealType: type, ingredientName });
        setIngredientModalOpen(true);
        setSwapLoading(true);
        setIngredientOptions([]);

        try {
            const menuId = menu.id || "current";
            const options = await api.swapIngredient(menuId, {
                day_index: dayIndex,
                meal_type: type,
                ingredient_name: ingredientName
            });
            setIngredientOptions(options);
        } catch (err) {
            console.error(err);
        } finally {
            setSwapLoading(false);
        }
    };

    const handleConfirmIngredientSwap = (newName) => {
        // Optimistic UI update: just rename the ingredient in the local state.
        // A full recalculation requires hitting the backend, but for UX speed:
        const newMenu = { ...menu };
        const meal = newMenu.days[activeIngredientSwap.dayIndex].meals[activeIngredientSwap.mealType];

        meal.ingredients = meal.ingredients.map(ing => {
            if (typeof ing === 'string' && ing === activeIngredientSwap.ingredientName) return newName;
            if (ing.name === activeIngredientSwap.ingredientName) return { ...ing, name: newName };
            return ing;
        });

        setMenu(newMenu);
        setIngredientModalOpen(false);
        setActiveIngredientSwap(null);
    };

    const handleBoostMacroRequest = async (type, meal, dayIndex, targetMacro) => {
        setActiveBoost({ dayIndex, mealType: type });
        setBoostModalOpen(true);
        setSwapLoading(true);
        setBoostOptions([]);

        try {
            const menuId = menu.id || "current";
            const options = await api.boostMacro(menuId, {
                day_index: dayIndex,
                meal_type: type,
                target_macro: targetMacro
            });
            setBoostOptions(options);
        } catch (err) {
            console.error(err);
        } finally {
            setSwapLoading(false);
        }
    };

    const handleConfirmBoost = (opt) => {
        const newMenu = { ...menu };
        const meal = newMenu.days[activeBoost.dayIndex].meals[activeBoost.mealType];

        // Add the new ingredient
        meal.ingredients.push({
            name: opt.name,
            weight_g: opt.estimated_weight_g || 0,
            amount: opt.amount_description
        });

        // Optimistically add protein
        meal.protein_g = Number((meal.protein_g + (opt.macro_boost_g || 0)).toFixed(1));

        if (!meal.tags) meal.tags = [];
        if (!meal.tags.includes("High Protein")) meal.tags.push("High Protein");

        setMenu(newMenu);
        setBoostModalOpen(false);
        setActiveBoost(null);
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

            <NutritionSpotlight />

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
                                    onSwapIngredient={(t, ingName) => handleIngredientSwapRequest(t, meal, idx, ingName)}
                                    onBoostMacro={(t, macro) => handleBoostMacroRequest(t, meal, idx, macro)}
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

            <IngredientSwapModal
                isOpen={isIngredientModalOpen}
                ingredient={activeIngredientSwap?.ingredientName}
                loading={swapLoading}
                options={ingredientOptions}
                onClose={() => setIngredientModalOpen(false)}
                onSelect={handleConfirmIngredientSwap}
            />

            <MacroBoostModal
                isOpen={isBoostModalOpen}
                loading={swapLoading}
                options={boostOptions}
                onClose={() => setBoostModalOpen(false)}
                onSelect={handleConfirmBoost}
            />
        </main>
    );
}
