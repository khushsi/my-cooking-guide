"use client";

import { useState, useEffect } from "react";
import { api } from "../../lib/api";
import styles from "./page.module.css";

export default function GroceryListPage() {
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [isSyncing, setIsSyncing] = useState(false);

    useEffect(() => {
        fetchItems();
    }, []);

    const fetchItems = async () => {
        try {
            const data = await api.getGroceryList();
            setItems(data.items || []);
        } catch (err) {
            setError("Failed to load your grocery list");
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleToggleCheck = async (item) => {
        try {
            const newChecked = !item.is_checked;
            // Optimistic update
            setItems(prev => prev.map(i =>
                i.id === item.id ? { ...i, is_checked: newChecked } : i
            ).sort((a, b) => {
                if (a.is_checked === b.is_checked) return 0;
                return a.is_checked ? 1 : -1;
            }));

            await api.updateGroceryItem(item.id, { is_checked: newChecked });
        } catch (err) {
            console.error("Failed to update item", err);
            fetchItems();
        }
    };

    const handleDelete = async (id) => {
        try {
            setItems(prev => prev.filter(i => i.id !== id));
            await api.deleteGroceryItem(id);
        } catch (err) {
            console.error("Failed to delete item", err);
            fetchItems();
        }
    };

    const handleSync = async () => {
        setIsSyncing(true);
        try {
            const res = await api.syncGroceryFromMenu("current");
            setItems(res.items || []);
            alert("Synced from your weekly menu!");
        } catch (err) {
            console.error("Failed to sync", err);
            setError("Could not sync from menu. High five for trying!");
        } finally {
            setIsSyncing(false);
        }
    };

    // Group items by category
    const groupedItems = items.reduce((acc, item) => {
        const cat = item.category || "General";
        if (!acc[cat]) acc[cat] = [];
        acc[cat].push(item);
        return acc;
    }, {});

    const categories = Object.keys(groupedItems).sort();

    if (loading) return <div className={styles.loading}>Preparing your shopping list...</div>;

    return (
        <main className={styles.container}>
            <div className={styles.header}>
                <h1>Shopping List</h1>
                <div style={{ display: 'flex', gap: '12px' }}>
                    <button
                        className={styles.addButton}
                        onClick={handleSync}
                        disabled={isSyncing}
                    >
                        {isSyncing ? "Syncing..." : "Sync from Menu"}
                    </button>
                    <button
                        className={styles.addButton}
                        onClick={() => alert("Add manual item coming soon!")}
                    >
                        + Add Item
                    </button>
                </div>
            </div>

            {error && <div className={styles.error}>{error}</div>}

            {items.length === 0 ? (
                <div className={styles.emptyState}>
                    <p>Your shopping list is empty. Plans for dinner?</p>
                    <button className={styles.addButton} onClick={handleSync}>
                        Import from Menu
                    </button>
                </div>
            ) : (
                categories.map(category => (
                    <section key={category} className={styles.categorySection}>
                        <h2 className={styles.categoryTitle}>{category}</h2>
                        <div className={styles.list}>
                            {groupedItems[category].map(item => (
                                <div
                                    key={item.id}
                                    className={`${styles.itemCard} ${item.is_checked ? styles.checked : ''}`}
                                >
                                    <div className={styles.checkboxWrapper} onClick={() => handleToggleCheck(item)}>
                                        <div className={`${styles.checkbox} ${item.is_checked ? styles.checked : ''}`} />
                                    </div>
                                    <div className={styles.itemInfo}>
                                        <h3 className={styles.itemName}>{item.name}</h3>
                                        <div className={styles.itemQuantity}>
                                            {item.quantity}
                                            {item.is_from_menu && <span className={styles.itemBadge}>From Menu</span>}
                                        </div>
                                    </div>
                                    <button
                                        className={styles.deleteBtn}
                                        onClick={() => handleDelete(item.id)}
                                    >
                                        Remove
                                    </button>
                                </div>
                            ))}
                        </div>
                    </section>
                ))
            )}
        </main>
    );
}
