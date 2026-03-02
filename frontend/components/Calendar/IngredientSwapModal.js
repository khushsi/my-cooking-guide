"use client";
import styles from "../../app/calendar/page.module.css";
import { useState, useEffect } from "react";

export default function IngredientSwapModal({ isOpen, ingredient, loading, options, onClose, onSelect }) {
    if (!isOpen) return null;

    return (
        <div className={styles.modalOverlay} onClick={onClose}>
            <div className={styles.modalContent} onClick={e => e.stopPropagation()}>
                <div className={styles.modalHeader}>
                    <h2>Swap "{ingredient}"</h2>
                    <button className={styles.closeBtn} onClick={onClose}>×</button>
                </div>

                <p style={{ color: "var(--text-dim)", marginBottom: "1rem" }}>
                    Select a healthier or preferred alternative to replace <strong>{ingredient}</strong> in this recipe.
                </p>

                {loading ? (
                    <div style={{ padding: "2rem", textAlign: "center" }}>
                        <div className="spinner" style={{ margin: "0 auto", width: 40, height: 40 }} />
                        <p style={{ marginTop: "1rem", color: "var(--text-dim)" }}>AI is analyzing alternatives...</p>
                    </div>
                ) : (
                    <div className={styles.optionsList} style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                        {options && options.length > 0 ? (
                            options.map((opt, idx) => (
                                <div
                                    key={idx}
                                    className="glass-card"
                                    style={{ padding: "12px 16px", cursor: "pointer", transition: "all 0.2s ease" }}
                                    onClick={() => onSelect(opt.name)}
                                    // simple hover effect inline
                                    onMouseOver={e => e.currentTarget.style.transform = "translateY(-2px)"}
                                    onMouseOut={e => e.currentTarget.style.transform = "none"}
                                >
                                    <h4 style={{ margin: "0 0 4px 0", color: "#6c5ce7" }}>{opt.name}</h4>
                                    <p style={{ margin: 0, fontSize: "0.85rem", color: "var(--text-dim)" }}>{opt.reason}</p>
                                </div>
                            ))
                        ) : (
                            <p style={{ color: "var(--error-color)" }}>Failed to find alternatives. Please try again.</p>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
