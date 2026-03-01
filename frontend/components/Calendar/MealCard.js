"use client";
import styles from "../../app/calendar/page.module.css";

const ICONS = {
    breakfast: "🌅",
    lunch: "☀️",
    dinner: "🌙",
    snack: "🍿"
};

export default function MealCard({ type, meal, onSwap }) {
    if (!meal) return null;

    return (
        <div className={styles.mealCard}>
            <div className={styles.mealHeader}>
                <span className={styles.mealIcon}>{ICONS[type]}</span>
                <span className={styles.mealType}>{type.charAt(0).toUpperCase() + type.slice(1)}</span>
                <button
                    className={styles.swapBtn}
                    onClick={() => onSwap(type, meal)}
                    title="Swap this meal"
                >
                    🔄
                </button>
            </div>
            <h4 className={styles.mealName}>{meal.name}</h4>
            <div className={styles.mealMeta}>
                <span>🔥 {meal.calories} kcal</span>
                <span>💪 {meal.protein_g}g P</span>
            </div>
            {meal.tags && (
                <div className={styles.mealTags}>
                    {meal.tags.slice(0, 2).map(tag => (
                        <span key={tag} className={styles.tag}>{tag}</span>
                    ))}
                </div>
            )}
        </div>
    );
}
