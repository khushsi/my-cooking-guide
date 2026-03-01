"use client";
import styles from "../../app/onboarding/page.module.css";

const INGREDIENT_CATEGORIES = [
    { name: "Proteins", items: ["Chicken", "Salmon", "Tofu", "Paneer", "Eggs", "Beef", "Pork", "Shrimp", "Lentils", "Black Beans", "Chickpeas"] },
    { name: "Carbs & Grains", items: ["Rice", "Pasta", "Quinoa", "Sweet Potato", "Potato", "Bread", "Oats", "Couscous", "Roti", "Naan"] },
    { name: "Vegetables", items: ["Broccoli", "Spinach", "Bell Pepper", "Onion", "Garlic", "Mushroom", "Asparagus", "Carrots", "Tomato", "Zucchini"] },
    { name: "Pantry Staples", items: ["Olive Oil", "Salt", "Black Pepper", "Soy Sauce", "Canned Tomatoes", "Coconut Milk", "Curry Powder", "Garam Masala", "Turmeric"] }
];

export default function PantryStep({
    pantryItems, togglePantryItem,
    searchTerm, setSearchTerm, addSearchItem,
    onBack, onNext
}) {
    return (
        <div className={`${styles.stepContent} animate-slide-up`}>
            <h1 className="section-title">What&apos;s in your kitchen?</h1>
            <p className="section-subtitle">Pick 3–5 items you&apos;d like to use this week. We&apos;ll build around them.</p>

            <div className={styles.field}>
                <div className={styles.inputRow}>
                    <input
                        className="input"
                        placeholder="Search or add an ingredient..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        onKeyDown={(e) => e.key === "Enter" && addSearchItem()}
                    />
                    <button className="btn btn-secondary" onClick={addSearchItem}>Add</button>
                </div>
            </div>

            {pantryItems.length > 0 && (
                <div className={styles.field}>
                    <label className={styles.label}>Your items ({pantryItems.length})</label>
                    <div className={styles.chipRow}>
                        {pantryItems.map((item) => (
                            <span key={item} className="chip active">
                                {item}
                                <span className="remove" onClick={() => togglePantryItem(item)}>×</span>
                            </span>
                        ))}
                    </div>
                </div>
            )}

            <div className={styles.field}>
                <label className={styles.label}>Popular ingredients</label>
                <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem", marginTop: "1rem" }}>
                    {INGREDIENT_CATEGORIES.map((cat) => (
                        <div key={cat.name}>
                            <h4 style={{ fontSize: "0.9rem", color: "var(--text-dim)", marginBottom: "0.75rem" }}>{cat.name}</h4>
                            <div className={styles.chipRow}>
                                {cat.items.filter(i => !pantryItems.includes(i)).map(item => (
                                    <button key={item} className="chip" onClick={() => togglePantryItem(item)}>+ {item}</button>
                                ))}
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            <div className={styles.buttonRow}>
                <button className="btn btn-ghost" onClick={onBack}>← Back</button>
                <button className="btn btn-primary btn-lg" onClick={onNext}>Next — Generate! ✨</button>
            </div>
        </div>
    );
}
