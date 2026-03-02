"use client";
import styles from "../../app/calendar/page.module.css";

const ICONS = {
    breakfast: "🌅",
    lunch: "☀️",
    dinner: "🌙",
    snack: "🍿"
};

export default function MealCard({ type, meal, onSwap, onSwapIngredient, onBoostMacro }) {
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

            {/* AI Macro Boost conditional UI */}
            {meal.protein_g < 20 && onBoostMacro && (
                <button
                    className="btn btn-outline"
                    style={{
                        padding: "4px 8px", fontSize: "0.8rem",
                        display: "flex", alignItems: "center", gap: "6px",
                        marginTop: "8px", borderColor: "rgba(108, 92, 231, 0.4)", color: "#6c5ce7",
                        width: "fit-content"
                    }}
                    onClick={() => onBoostMacro(type, 'protein')}
                    title="Suggest high-protein additions to this meal"
                >
                    <span style={{ fontSize: "1rem" }}>✨</span> Protein Boost
                </button>
            )}

            {/* Interactive Ingredients List */}
            {meal.ingredients && (
                <div style={{ marginTop: "1rem" }}>
                    <div style={{ fontSize: "0.8rem", color: "var(--text-dim)", marginBottom: "4px" }}>Ingredients (Click to swap):</div>
                    <ul style={{ listStyle: "none", padding: 0, margin: 0, fontSize: "0.85rem", color: "var(--text-color)" }}>
                        {meal.ingredients.map((ing, idx) => {
                            const name = typeof ing === 'string' ? ing : ing.name;
                            return (
                                <li
                                    key={idx}
                                    style={{
                                        padding: "4px 6px", margin: "2px 0", cursor: "pointer",
                                        borderRadius: "6px", background: "rgba(0,0,0,0.02)",
                                        display: "flex", alignItems: "center", gap: "6px",
                                        transition: "background 0.2s ease"
                                    }}
                                    onMouseOver={(e) => e.currentTarget.style.background = "rgba(108, 92, 231, 0.1)"}
                                    onMouseOut={(e) => e.currentTarget.style.background = "rgba(0,0,0,0.02)"}
                                    onClick={() => onSwapIngredient && onSwapIngredient(type, name)}
                                    title={`Click to find an alternative for ${name}`}
                                >
                                    <span style={{ fontSize: "0.7rem", opacity: 0.5 }}>🔄</span> {name}
                                </li>
                            );
                        })}
                    </ul>
                </div>
            )}

            {meal.tags && (
                <div className={styles.mealTags} style={{ marginTop: "1rem" }}>
                    {meal.tags.slice(0, 2).map(tag => (
                        <span key={tag} className={styles.tag}>{tag}</span>
                    ))}
                </div>
            )}
        </div>
    );
}
