"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function DashboardPage() {
    const router = useRouter();

    useEffect(() => {
        // For now, the dashboard is synonymous with the calendar view.
        // We redirect here to provide a seamless experience while the full dashboard is built.
        router.push("/calendar");
    }, [router]);

    return (
        <div style={{
            display: "flex",
            justifyContent: "center",
            alignSelf: "center",
            height: "100vh",
            flexDirection: "column",
            alignItems: "center",
            background: "var(--bg-dark)",
            color: "white"
        }}>
            <div className="spinner" style={{ width: 40, height: 40, marginBottom: 20 }} />
            <p>Accessing your kitchen dashboard...</p>
        </div>
    );
}
