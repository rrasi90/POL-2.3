"use client";

import { getLastCorrelationId } from "@pol/api-client";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  const correlationId = getLastCorrelationId();

  return (
    <html lang="fa" dir="rtl">
      <body
        style={{
          margin: 0,
          minHeight: "100vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontFamily: "var(--font-vazirmatn), system-ui, sans-serif",
          background: "#f7f7f8",
          color: "#111827",
          textAlign: "center",
          padding: "24px",
        }}
      >
        <main style={{ maxWidth: "28rem" }}>
          <h1 style={{ fontSize: "1.25rem", fontWeight: 800 }}>
            خطای غیرمنتظره در برنامه
          </h1>
          <p style={{ fontSize: "0.875rem", lineHeight: 1.9, color: "#4b5563" }}>
            صفحه به‌درستی بارگذاری نشد. داده‌ای ثبت یا تغییر نکرده است. لطفاً دوباره تلاش کنید.
          </p>
          {correlationId || error.digest ? (
            <p style={{ fontSize: "0.75rem", color: "#6b7280" }}>
              کد پیگیری:{" "}
              <span style={{ fontFamily: "monospace" }}>{correlationId ?? error.digest}</span>
            </p>
          ) : null}
          <button
            type="button"
            onClick={() => reset()}
            style={{
              marginTop: "1rem",
              padding: "0.5rem 1.25rem",
              borderRadius: "0.75rem",
              border: "none",
              background: "#111827",
              color: "#ffffff",
              fontFamily: "inherit",
              fontSize: "0.875rem",
              cursor: "pointer",
            }}
          >
            تلاش دوباره
          </button>
        </main>
      </body>
    </html>
  );
}
