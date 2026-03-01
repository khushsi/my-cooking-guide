"use client";
import { useState } from "react";
import styles from "../../app/calendar/page.module.css";

export default function SwapModal({ meal, isOpen, onClose, onConfirm, loading }) {
    const [reason, setReason] = useState("");

    if (!isOpen) return null;

    return (
        <div className={styles.modalOverlay} onClick={onClose}>
            <div className={styles.modalContent} onClick={e => e.stopPropagation()}>
                <button className={styles.closeModal} onClick={onClose}>×</button>

                <h2 className="section-title" style={{ fontSize: "1.5rem" }}>Swap Meal</h2>
                <p className="section-subtitle">Not feeling <strong>{meal?.name}</strong>? Tell us why and we&apos;ll find a better fit.</p>

                <div className={styles.swapOptions}>
                    {[
                        "Too complex to cook",
                        "Don't have the ingredients",
                        "Just not in the mood",
                        "Want something healthier",
                        "Want something faster"
                    ].map(r => (
                        <button
                            key={r}
                            className={`chip ${reason === r ? "active" : ""}`}
                            onClick={() => setReason(r)}
                        >
                            {r}
                        </button>
                    ))}
                </div>

                <textarea
                    className="input"
                    placeholder="Or type a custom reason (e.g. 'I want something with more spice')"
                    value={reason}
                    onChange={(e) => setReason(e.target.value)}
                    rows={3}
                    style={{ marginTop: "1rem" }}
                />

                <div className={styles.modalActions} style={{ marginTop: "2rem", display: "flex", gap: "1rem" }}>
                    <button className="btn btn-ghost" onClick={onClose} style={{ flex: 1 }}>Cancel</button>
                    <button
                        className="btn btn-primary"
                        onClick={() => onConfirm(reason)}
                        disabled={loading}
                        style={{ flex: 2 }}
                    >
                        {loading ? <div className="spinner" /> : "🪄 Find Replacement"}
                    </button>
                </div>
            </div>
        </div>
    );
}
