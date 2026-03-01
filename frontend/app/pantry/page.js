"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { api } from "../../lib/api";
import styles from "./page.module.css";

export default function PantryPage() {
    const router = useRouter();
    const [pantry, setPantry] = useState([]);
    const [loading, setLoading] = useState(true);
    const [uploading, setUploading] = useState(false);
    const [error, setError] = useState("");

    useEffect(() => {
        fetchPantry();
    }, []);

    const fetchPantry = async () => {
        try {
            const data = await api.getPantry();
            setPantry(data || []);
        } catch (err) {
            setError("Failed to load pantry items");
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleUpdateQuantity = async (id, newQuantity) => {
        if (newQuantity < 0) return;

        try {
            // Optimistic update
            setPantry(prev => prev.map(item =>
                item.id === id ? { ...item, quantity: newQuantity } : item
            ));

            await api.updatePantryItem(id, { quantity: newQuantity });
        } catch (err) {
            console.error("Failed to update quantity", err);
            // Revert on error
            fetchPantry();
        }
    };

    const handleDelete = async (id) => {
        if (!confirm("Are you sure you want to delete this item?")) return;

        try {
            // Optimistic update
            setPantry(prev => prev.filter(item => item.id !== id));
            await api.deletePantryItem(id);
        } catch (err) {
            console.error("Failed to delete item", err);
            fetchPantry();
        }
    };

    const handleFileUpload = async (e) => {
        const file = e.target.files?.[0];
        if (!file) return;

        setUploading(true);
        setError("");
        try {
            await api.scanPantryImage(file);
            await fetchPantry();
        } catch (err) {
            setError(err.message || "Failed to scan image");
        } finally {
            setUploading(false);
            e.target.value = ""; // Reset input
        }
    };

    // Group items by category
    const groupedPantry = pantry.reduce((acc, item) => {
        const cat = item.category || "Other";
        if (!acc[cat]) acc[cat] = [];
        acc[cat].push(item);
        return acc;
    }, {});

    const categories = Object.keys(groupedPantry).sort();

    if (loading) return <div className={styles.loading}>Loading your pantry...</div>;

    return (
        <main className={styles.container}>
            <div className={styles.header}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
                    <h1>My Inventory</h1>
                    <nav style={{ display: 'flex', gap: '15px' }}>
                        <button className="btn-link" onClick={() => router.push("/calendar")}>Calendar</button>
                        <button className="btn-link" onClick={() => router.push("/grocery-list")}>Grocery List</button>
                    </nav>
                </div>
                <div style={{ display: 'flex', gap: '10px' }}>
                    <input
                        type="file"
                        accept="image/*"
                        id="magic-scan"
                        style={{ display: 'none' }}
                        onChange={handleFileUpload}
                        disabled={uploading}
                    />
                    <label
                        htmlFor="magic-scan"
                        className={styles.addButton}
                        style={{ backgroundColor: '#6c5ce7', cursor: uploading ? 'not-allowed' : 'pointer', opacity: uploading ? 0.7 : 1, width: 'auto' }}
                    >
                        {uploading ? "✨ Scanning..." : "✨ Magic Scan"}
                    </label>
                    <button className={styles.addButton} onClick={() => alert("Add item modal coming soon!")}>
                        + Add Manually
                    </button>
                </div>
            </div>

            {error && <div className={styles.error}>{error}</div>}

            {categories.length === 0 ? (
                <div className={styles.emptyState}>
                    <p>Your pantry is empty. Start by adding some items!</p>
                </div>
            ) : (
                categories.map(category => (
                    <section key={category} className={styles.categorySection}>
                        <h2 className={styles.categoryTitle}>{category}</h2>
                        <div className={styles.grid}>
                            {groupedPantry[category].map(item => (
                                <div key={item.id} className={styles.card}>
                                    <div className={styles.cardInfo}>
                                        <h3>{item.name}</h3>
                                        <div className={styles.quantityControls}>
                                            <button
                                                className={styles.qtyBtn}
                                                onClick={() => handleUpdateQuantity(item.id, item.quantity - 1)}
                                            >
                                                -
                                            </button>
                                            <div className={styles.qtyDisplay}>
                                                {item.quantity}
                                                <span className={styles.unit}>{item.unit}</span>
                                            </div>
                                            <button
                                                className={styles.qtyBtn}
                                                onClick={() => handleUpdateQuantity(item.id, item.quantity + 1)}
                                            >
                                                +
                                            </button>
                                        </div>
                                    </div>
                                    <div className={styles.actions}>
                                        <button
                                            className={styles.deleteBtn}
                                            onClick={() => handleDelete(item.id)}
                                        >
                                            Delete
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </section>
                ))
            )}
        </main>
    );
}
