"use client";
import styles from "../../app/calendar/page.module.css";
import { useState, useEffect } from "react";

export default function MacroBoostModal({ isOpen, loading, options, onClose, onSelect }) {
    if (!isOpen) return null;

    return (
        <div className={styles.modalOverlay} onClick={onClose}>
            <div className={styles.modalContent} onClick={e => e.stopPropagation()}>
                <div className={styles.modalHeader}>
                    <h2>✨ Protein Boosts</h2>
                    <button className={styles.closeBtn} onClick={onClose}>×</button>
                </div>

                <p style={{ color: "var(--text-dim)", marginBottom: "1rem" }}>
                    This meal is a bit low in protein. Here are some seamless additions.
                </p>

                {loading ? (
                    <div style={{ padding: "2rem", textAlign: "center" }}>
                        <div className="spinner" style={{ margin: "0 auto", width: 40, height: 40 }} />
                        <p style={{ marginTop: "1rem", color: "var(--text-dim)" }}>Finding perfect pairings...</p>
                    </div>
                ) : (
                    <div className={styles.optionsList} style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                        {options && options.length > 0 ? (
                            options.map((opt, idx) => (
                                <div
                                    key={idx}
                                    className="glass-card"
                                    style={{ padding: "12px 16px", cursor: "pointer", transition: "all 0.2s ease" }}
                                    onClick={() => onSelect(opt)}
                                    onMouseOver={e => e.currentTarget.style.transform = "translateY(-2px)"}
                                    onMouseOut={e => e.currentTarget.style.transform = "none"}
                                >
                                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "4px" }}>
                                        <h4 style={{ margin: 0, color: "#6c5ce7" }}>{opt.name}</h4>
                                        <div style={{ background: "rgba(108, 92, 231, 0.1)", color: "#6c5ce7", padding: "2px 8px", borderRadius: "12px", fontSize: "0.75rem", fontWeight: "bold" }}>
                                            +{opt.macro_boost_g}g Protein
                                        </div>
                                    </div>
                                    <p style={{ margin: 0, fontSize: "0.85rem", color: "var(--text-dim)" }}>{opt.amount_description}</p>
                                </div>
                            ))
                        ) : (
                            <p style={{ color: "var(--error-color)" }}>No suggestions available right now.</p>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
