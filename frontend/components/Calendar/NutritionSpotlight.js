"use client";
import { useState, useEffect } from "react";

const SPOTLIGHTS = [
    {
        name: "Hemp Hearts",
        emoji: "🌿",
        description: "A complete plant protein, rich in Omega-3s.",
        protein: "10g per 3 tbsp",
        color: "linear-gradient(135deg, #00b894 0%, #00cec9 100%)"
    },
    {
        name: "Edamame",
        emoji: "🫛",
        description: "Incredibly high in protein and fiber, perfect for snacking or salads.",
        protein: "17g per cup",
        color: "linear-gradient(135deg, #27ae60 0%, #2ecc71 100%)"
    },
    {
        name: "Quinoa",
        emoji: "🌾",
        description: "A versatile pseudo-cereal that forms a complete protein profile.",
        protein: "8g per cup",
        color: "linear-gradient(135deg, #e17055 0%, #fdcb6e 100%)"
    }
];

export default function NutritionSpotlight() {
    const [spotlight, setSpotlight] = useState(null);

    useEffect(() => {
        // Just pick a random one for now to simulate a "Weekly Spotlight"
        const index = new Date().getDay() % SPOTLIGHTS.length;
        setSpotlight(SPOTLIGHTS[index]);
    }, []);

    if (!spotlight) return null;

    return (
        <div style={{
            background: spotlight.color,
            borderRadius: "16px",
            padding: "20px",
            color: "white",
            marginBottom: "2rem",
            display: "flex",
            alignItems: "center",
            gap: "20px",
            boxShadow: "0 8px 16px rgba(0,0,0,0.1)",
            position: "relative",
            overflow: "hidden"
        }}>
            <div style={{
                position: "absolute",
                right: "-20px",
                bottom: "-30px",
                fontSize: "8rem",
                opacity: 0.1,
                userSelect: "none"
            }}>
                {spotlight.emoji}
            </div>

            <div style={{ flex: 1, zIndex: 1 }}>
                <div style={{ textTransform: "uppercase", fontSize: "0.8rem", letterSpacing: "1px", opacity: 0.9, marginBottom: "4px" }}>
                    ⭐ Super-Ingredient of the Week
                </div>
                <h3 style={{ margin: "0 0 8px 0", fontSize: "1.5rem" }}>{spotlight.name}</h3>
                <p style={{ margin: "0 0 12px 0", fontSize: "0.95rem", opacity: 0.9 }}>{spotlight.description}</p>
                <div style={{ display: "inline-block", background: "rgba(255,255,255,0.2)", padding: "4px 10px", borderRadius: "20px", fontSize: "0.85rem", fontWeight: "bold" }}>
                    💪 {spotlight.protein}
                </div>
            </div>

            <div style={{ zIndex: 1, display: "none" }}>
                {/* Future enhancement: add an action button here */}
            </div>
        </div>
    );
}
