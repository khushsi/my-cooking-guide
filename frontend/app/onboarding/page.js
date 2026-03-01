"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { api } from "../../lib/api";
import { storage } from "../../lib/storage";
import styles from "./page.module.css";

import PersonaStep from "../../components/Onboarding/PersonaStep";
import BasicsStep from "../../components/Onboarding/BasicsStep";
import PantryStep from "../../components/Onboarding/PantryStep";
import MagicStep from "../../components/Onboarding/MagicStep";

export default function OnboardingPage() {
    const router = useRouter();
    const [step, setStep] = useState(0);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    // State management
    const [personas, setPersonas] = useState([]);
    const [selectedPersonaId, setSelectedPersonaId] = useState("");
    const [householdSize, setHouseholdSize] = useState(2);
    const [dietType, setDietType] = useState("omnivore");
    const [allergies, setAllergies] = useState([]);
    const [customAllergy, setCustomAllergy] = useState("");
    const [mealTypes, setMealTypes] = useState(["breakfast", "lunch", "dinner"]);
    const [pantryItems, setPantryItems] = useState([]);
    const [searchTerm, setSearchTerm] = useState("");

    // Load state from session storage on mount
    useEffect(() => {
        const savedStep = storage.session.get("onboarding_step");
        if (savedStep !== null) setStep(savedStep);

        const savedData = storage.session.get("onboarding_data");
        if (savedData) {
            if (savedData.selectedPersonaId) setSelectedPersonaId(savedData.selectedPersonaId);
            if (savedData.householdSize) setHouseholdSize(savedData.householdSize);
            if (savedData.dietType) {
                console.log("Onboarding: Loading dietType from storage:", savedData.dietType);
                setDietType(savedData.dietType);
            }
            if (savedData.allergies) setAllergies(savedData.allergies);
            if (savedData.mealTypes) setMealTypes(savedData.mealTypes);
            if (savedData.pantryItems) setPantryItems(savedData.pantryItems);
        }
    }, []);

    // Persist state to session storage
    useEffect(() => {
        storage.session.set("onboarding_step", step);
        storage.session.set("onboarding_data", {
            selectedPersonaId, householdSize, dietType, allergies, mealTypes, pantryItems
        });
    }, [step, selectedPersonaId, householdSize, dietType, allergies, mealTypes, pantryItems]);

    useEffect(() => {
        api.getPersonaTemplates()
            .then(res => setPersonas(res.templates || []))
            .catch(err => console.error("Failed to fetch personas", err));
    }, []);

    const toggleAllergy = (allergy) => {
        setAllergies(prev => prev.includes(allergy) ? prev.filter(a => a !== allergy) : [...prev, allergy]);
    };

    const addCustomAllergy = () => {
        if (customAllergy.trim()) {
            if (!allergies.includes(customAllergy.trim())) {
                setAllergies([...allergies, customAllergy.trim()]);
            }
            setCustomAllergy("");
        }
    };

    const toggleMealType = (meal) => {
        setMealTypes(prev => {
            if (prev.includes(meal)) {
                return prev.length > 1 ? prev.filter(m => m !== meal) : prev;
            }
            return [...prev, meal];
        });
    };

    const togglePantryItem = (item) => {
        setPantryItems(prev => prev.includes(item) ? prev.filter(i => i !== item) : [...prev, item]);
    };

    const addSearchItem = () => {
        if (searchTerm.trim() && !pantryItems.includes(searchTerm.trim())) {
            setPantryItems([...pantryItems, searchTerm.trim()]);
            setSearchTerm("");
        }
    };

    const handlePersonaSelect = (personaId) => {
        console.log("Onboarding: Persona selected:", personaId);
        setSelectedPersonaId(personaId);
        if (personaId !== "scratch") {
            const p = personas.find(p => p.id === personaId);
            if (p) {
                console.log("Onboarding: Applying persona defaults:", p.defaults.dietType);
                setDietType(p.defaults.dietType || "omnivore");
                setAllergies(p.defaults.allergies || []);
                setPantryItems(p.defaults.pantryItems || []);
            }
        }
    };

    const handleGenerate = async () => {
        setLoading(true);
        setError("");
        console.log("Onboarding: Generating menu with diet:", dietType);
        try {
            let token = storage.get("token");
            if (!token || token.startsWith("demo-token")) {
                const demoToken = `demo-token-${Date.now()}`;
                storage.set("token", demoToken);
                storage.set("demoPreferences", { dietType, mealTypes, allergies, pantryItems });

                setError("Demo mode: Redirecting to calendar preview...");
                setTimeout(() => {
                    storage.session.clear();
                    router.push("/calendar");
                }, 2000);
                return;
            }

            await api.completeOnboarding({
                selected_persona_id: selectedPersonaId !== "scratch" ? selectedPersonaId : null,
                household_size: householdSize,
                diet_type: dietType,
                allergies,
                pantry_staples: pantryItems,
                meal_types: mealTypes,
            });

            storage.session.clear();
            router.push("/calendar");
        } catch (err) {
            console.error("Onboarding failed", err);
            setError("Failed to generate menu. Please try again or check your API keys.");
            setLoading(false);
        }
    };

    return (
        <main className={styles.container}>
            <div className={styles.stepIndicator}>
                {[0, 1, 2, 3].map((s) => (
                    <div key={s} className={`${styles.stepDot} ${s <= step ? styles.stepActive : ""} ${s < step ? styles.stepDone : ""}`}>
                        {s < step ? "✓" : (s === 0 ? "P" : s)}
                    </div>
                ))}
            </div>

            {step === 0 && (
                <PersonaStep
                    personas={personas}
                    selectedPersonaId={selectedPersonaId}
                    onSelect={handlePersonaSelect}
                    onNext={() => setStep(1)}
                />
            )}

            {step === 1 && (
                <BasicsStep
                    householdSize={householdSize} setHouseholdSize={setHouseholdSize}
                    dietType={dietType} setDietType={setDietType}
                    mealTypes={mealTypes} toggleMealType={toggleMealType}
                    allergies={allergies} toggleAllergy={toggleAllergy}
                    customAllergy={customAllergy} setCustomAllergy={setCustomAllergy}
                    addCustomAllergy={addCustomAllergy} onNext={() => setStep(2)}
                />
            )}

            {step === 2 && (
                <PantryStep
                    pantryItems={pantryItems} togglePantryItem={togglePantryItem}
                    searchTerm={searchTerm} setSearchTerm={setSearchTerm}
                    addSearchItem={addSearchItem} onBack={() => setStep(1)}
                    onNext={() => setStep(3)}
                />
            )}

            {step === 3 && (
                <MagicStep
                    householdSize={householdSize} dietType={dietType}
                    mealTypes={mealTypes} allergies={allergies}
                    pantryItems={pantryItems} loading={loading}
                    error={error} onBack={() => setStep(2)}
                    onGenerate={handleGenerate}
                />
            )}
        </main>
    );
}
