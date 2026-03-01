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

const COMMON_ALLERGIES = [
    "Peanuts", "Tree Nuts", "Milk", "Eggs", "Wheat",
    "Soy", "Fish", "Shellfish", "Sesame", "Gluten",
];

export default function BasicsStep({
    householdSize, setHouseholdSize,
    dietType, setDietType,
    mealTypes, toggleMealType,
    allergies, toggleAllergy,
    customAllergy, setCustomAllergy, addCustomAllergy,
    onNext
}) {
    return (
        <div className={`${styles.stepContent} animate-slide-up`}>
            <h1 className="section-title">Let&apos;s get to know you</h1>
            <p className="section-subtitle">Just a few basics so we can create your perfect meal plan.</p>

            <div className={styles.field}>
                <label className={styles.label}>Household size</label>
                <div className={styles.counterRow}>
                    <button className="btn btn-secondary btn-icon" onClick={() => setHouseholdSize(Math.max(1, householdSize - 1))} aria-label="Decrease household size">−</button>
                    <span className={styles.counterValue} aria-live="polite">{householdSize}</span>
                    <button className="btn btn-secondary btn-icon" onClick={() => setHouseholdSize(householdSize + 1)} aria-label="Increase household size">+</button>
                </div>
            </div>

            <div className={styles.field}>
                <label className={styles.label}>Dietary baseline</label>
                <div className={styles.optionGrid}>
                    {DIET_OPTIONS.map((opt) => (
                        <button
                            key={opt.value}
                            className={`${styles.optionCard} ${dietType === opt.value ? styles.optionActive : ""}`}
                            onClick={() => {
                                console.log("BasicsStep: Setting diet to:", opt.value);
                                setDietType(opt.value);
                            }}
                            aria-pressed={dietType === opt.value}
                            aria-label={`Select ${opt.label} diet`}
                        >
                            <span className={styles.optionIcon}>{opt.icon}</span>
                            <span>{opt.label}</span>
                        </button>
                    ))}
                </div>
            </div>

            <div className={styles.field}>
                <label className={styles.label}>Which meals do you want to plan?</label>
                <div className={styles.chipRow}>
                    {MEAL_OPTIONS.map((opt) => (
                        <button
                            key={opt.value}
                            className={`chip ${mealTypes.includes(opt.value) ? "active" : ""}`}
                            onClick={() => toggleMealType(opt.value)}
                            aria-pressed={mealTypes.includes(opt.value)}
                            aria-label={`Toggle ${opt.label}`}
                        >
                            {opt.icon} {opt.label}
                        </button>
                    ))}
                </div>
            </div>

            <div className={styles.field}>
                <label className={styles.label}>Any allergies?</label>
                <div className={styles.chipRow}>
                    {COMMON_ALLERGIES.map((a) => (
                        <button
                            key={a}
                            className={`chip ${allergies.includes(a) ? "active" : ""}`}
                            onClick={() => toggleAllergy(a)}
                        >
                            {a}
                        </button>
                    ))}
                    {allergies.filter((a) => !COMMON_ALLERGIES.includes(a)).map((a) => (
                        <button key={a} className="chip active" onClick={() => toggleAllergy(a)}>
                            {a} <span className="remove">×</span>
                        </button>
                    ))}
                </div>
                <div className={styles.inputRow}>
                    <input
                        className="input"
                        placeholder="Add custom allergy..."
                        value={customAllergy}
                        onChange={(e) => setCustomAllergy(e.target.value)}
                        onKeyDown={(e) => e.key === "Enter" && addCustomAllergy()}
                    />
                    <button className="btn btn-secondary" onClick={addCustomAllergy}>Add</button>
                </div>
            </div>

            <button className="btn btn-primary btn-lg" style={{ width: "100%", marginTop: "1.5rem" }} onClick={onNext}>
                Next — Quick Pantry Scan →
            </button>
        </div>
    );
}
