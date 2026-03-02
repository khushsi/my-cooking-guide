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

const PROTEIN_OPTIONS = [
    "Tofu", "Paneer", "Seitan", "Lentils", "Chickpeas",
    "Black Beans", "Edamame", "Quinoa", "Hemp Hearts", "Eggs",
    "Chicken", "Fish", "Beef"
];

export default function BasicsStep({
    householdSize, setHouseholdSize,
    dietType, setDietType,
    mealTypes, toggleMealType,
    allergies, toggleAllergy,
    customAllergy, setCustomAllergy, addCustomAllergy,
    preferredProteins, togglePreferredProtein,
    avoidedProteins, toggleAvoidedProtein,
    sneakInProtein, setSneakInProtein,
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

            <div className={styles.field}>
                <label className={styles.label}>Advanced Nutrition: Protein Goals</label>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "1rem", padding: "1rem", backgroundColor: "rgba(108, 92, 231, 0.05)", borderRadius: "12px", border: "1px solid rgba(108, 92, 231, 0.2)" }}>
                    <div>
                        <div style={{ fontWeight: 600, color: "#2d3436" }}>✨ Sneak in Protein</div>
                        <div style={{ fontSize: "0.85rem", color: "#636e72", marginTop: "4px" }}>AI will actively blend high-protein ingredients into sauces & smoothies.</div>
                    </div>
                    <label style={{ display: "flex", alignItems: "center", cursor: "pointer" }}>
                        <div style={{ position: "relative" }}>
                            <input
                                type="checkbox"
                                checked={sneakInProtein}
                                onChange={(e) => setSneakInProtein(e.target.checked)}
                                style={{ opacity: 0, width: 0, height: 0 }}
                                aria-label="Toggle Sneak in Protein"
                            />
                            <div style={{
                                width: "44px", height: "24px",
                                backgroundColor: sneakInProtein ? "#6c5ce7" : "#dfe6e9",
                                borderRadius: "34px", transition: "0.4s",
                                display: "flex", alignItems: "center", padding: "2px"
                            }}>
                                <div style={{
                                    width: "20px", height: "20px",
                                    backgroundColor: "white", borderRadius: "50%",
                                    transition: "0.4s", transform: sneakInProtein ? "translateX(20px)" : "none"
                                }} />
                            </div>
                        </div>
                    </label>
                </div>

                <label className={styles.label} style={{ fontSize: "0.9rem", color: "#636e72" }}>Love these proteins (Click to prioritize):</label>
                <div className={styles.chipRow} style={{ marginBottom: "1rem" }}>
                    {PROTEIN_OPTIONS.map((p) => (
                        <button
                            key={`pref-${p}`}
                            className={`chip ${preferredProteins.includes(p) ? "active" : ""}`}
                            style={preferredProteins.includes(p) ? { backgroundColor: "#00b894", color: "white", borderColor: "#00b894" } : {}}
                            onClick={() => togglePreferredProtein(p)}
                        >
                            {preferredProteins.includes(p) ? "✓ " : ""}{p}
                        </button>
                    ))}
                </div>

                <label className={styles.label} style={{ fontSize: "0.9rem", color: "#636e72" }}>Avoid these proteins (Click to ban):</label>
                <div className={styles.chipRow}>
                    {PROTEIN_OPTIONS.map((p) => (
                        <button
                            key={`avoid-${p}`}
                            className={`chip ${avoidedProteins.includes(p) ? "active" : ""}`}
                            style={avoidedProteins.includes(p) ? { backgroundColor: "#d63031", color: "white", borderColor: "#d63031" } : {}}
                            onClick={() => toggleAvoidedProtein(p)}
                        >
                            {avoidedProteins.includes(p) ? "× " : ""}{p}
                        </button>
                    ))}
                </div>
            </div>

            <button className="btn btn-primary btn-lg" style={{ width: "100%", marginTop: "1.5rem" }} onClick={onNext}>
                Next — Quick Pantry Scan →
            </button>
        </div>
    );
}
