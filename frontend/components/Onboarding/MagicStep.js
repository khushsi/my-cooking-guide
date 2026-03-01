"use client";
import styles from "../../app/onboarding/page.module.css";

const DIET_OPTIONS = [
    { value: "omnivore", label: "Omnivore", icon: "🥩" },
    { value: "vegetarian", label: "Vegetarian", icon: "🥬" },
    { value: "vegan", label: "Vegan", icon: "🌱" },
    { value: "pescatarian", label: "Pescatarian", icon: "🐟" },
    { value: "keto", label: "Keto", icon: "🥑" },
    { value: "paleo", label: "Paleo", icon: "🍖" },
];

const MEAL_OPTIONS = [
    { value: "breakfast", label: "Breakfast", icon: "🌅" },
    { value: "lunch", label: "Lunch", icon: "☀️" },
    { value: "dinner", label: "Dinner", icon: "🌙" },
    { value: "snack", label: "Snacks", icon: "🍿" },
];

export default function MagicStep({
    householdSize, dietType, mealTypes, allergies, pantryItems,
    loading, error, onBack, onGenerate
}) {
    return (
        <div className={`${styles.stepContent} animate-slide-up`}>
            <div className={styles.magicSection}>
                <div className={styles.magicIcon}>✨</div>
                <h1 className="section-title">Ready to cook smarter?</h1>
                <p className="section-subtitle">We&apos;ll generate your personalized 7-day meal plan with a prep strategy.</p>

                <div className={`glass-card ${styles.summaryCard}`}>
                    <div className={styles.summaryRow}>
                        <span className={styles.summaryLabel}>Household</span>
                        <span className={styles.summaryValue}>{householdSize} {householdSize === 1 ? "person" : "people"}</span>
                    </div>
                    <div className={styles.summaryRow}>
                        <span className={styles.summaryLabel}>Diet</span>
                        <span className={styles.summaryValue}>
                            {DIET_OPTIONS.find(d => d.value === dietType)?.icon} {DIET_OPTIONS.find(d => d.value === dietType)?.label}
                        </span>
                    </div>
                    <div className={styles.summaryRow}>
                        <span className={styles.summaryLabel}>Meals</span>
                        <span className={styles.summaryValue}>
                            {mealTypes.map(m => MEAL_OPTIONS.find(o => o.value === m)?.label).join(", ")}
                        </span>
                    </div>
                    {allergies.length > 0 && (
                        <div className={styles.summaryRow}>
                            <span className={styles.summaryLabel}>Allergies</span>
                            <span className={styles.summaryValue}>{allergies.join(", ")}</span>
                        </div>
                    )}
                    <div className={styles.summaryRow}>
                        <span className={styles.summaryLabel}>Pantry</span>
                        <span className={styles.summaryValue}>{pantryItems.length > 0 ? pantryItems.join(", ") : "Standard staples"}</span>
                    </div>
                </div>

                {error && <p className={styles.error}>{error}</p>}

                <div className={styles.buttonRow}>
                    <button
                        className="btn btn-ghost"
                        onClick={onBack}
                        disabled={loading}
                        aria-label="Go back to pantry scan"
                    >← Back</button>
                    <button
                        className={`btn btn-primary btn-lg ${styles.generateBtn}`}
                        onClick={() => {
                            console.log("MagicStep: Generating with diet:", dietType);
                            onGenerate();
                        }}
                        disabled={loading}
                        aria-label={loading ? "Generating meal plan" : "Generate my meal plan"}
                    >
                        {loading ? <><div className="spinner" aria-hidden="true" /> Generating with AI...</> : <>🪄 Generate My Meal Plan</>}
                    </button>
                </div>
            </div>
        </div>
    );
}
