"use client";
import styles from "../../app/onboarding/page.module.css";

export default function PersonaStep({ personas, selectedPersonaId, onSelect, onNext }) {
    return (
        <div className={`${styles.stepContent} animate-slide-up`}>
            <h1 className="section-title">Who are we cooking for?</h1>
            <p className="section-subtitle">
                Select a starting persona to get tailored recommendations instantly, or build from scratch.
            </p>

            <div className={styles.personaGrid}>
                {personas.map(persona => (
                    <div
                        key={persona.id}
                        className={`${styles.personaCard} ${selectedPersonaId === persona.id ? styles.personaActive : ""}`}
                        onClick={() => onSelect(persona.id)}
                        role="button"
                        aria-pressed={selectedPersonaId === persona.id}
                        aria-label={`Select ${persona.title} persona`}
                    >
                        <div className={styles.personaIcon}>{persona.icon}</div>
                        <h3>{persona.title}</h3>
                        <p className={styles.personaSubtitle}>{persona.subtitle}</p>
                        <p className={styles.personaDesc}>{persona.description}</p>
                    </div>
                ))}

                <div
                    className={`${styles.personaCard} ${selectedPersonaId === "scratch" ? styles.personaActive : ""}`}
                    onClick={() => onSelect("scratch")}
                    role="button"
                    aria-pressed={selectedPersonaId === "scratch"}
                    aria-label="Select Custom persona"
                >
                    <div className={styles.personaIcon}>🛠️</div>
                    <h3>Custom</h3>
                    <p className={styles.personaSubtitle}>Build from scratch</p>
                    <p className={styles.personaDesc}>I'll enter all my preferences manually.</p>
                </div>
            </div>

            <button
                className="btn btn-primary btn-lg"
                style={{ width: "100%", marginTop: "2rem" }}
                onClick={onNext}
                disabled={!selectedPersonaId}
                id="next-step-0-btn"
                aria-label="Proceed to fine tuning"
            >
                Next — Fine Tuning →
            </button>
        </div>
    );
}
