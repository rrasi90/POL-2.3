"use client";

import { useState } from "react";
import { LoginForm } from "@/components/auth/LoginForm";
import { OtpVerifyForm } from "@/components/auth/OtpVerifyForm";
import { api } from "@/lib/api/client";

interface AuthResult {
  access_token?: string;
  refresh_token?: string;
}

interface SuccessEnvelope<T> {
  data?: T;
}

export default function AuthPage() {
  const [phoneNumber, setPhoneNumber] = useState("");
  const [step, setStep] = useState<"login" | "verify">("login");

  async function requestOtp(phone: string) {
    await api.post("/api/v1/auth/request-otp", { mobile_number: phone });
    setPhoneNumber(phone);
    setStep("verify");
  }

  async function verifyOtp(phone: string, code: string) {
    const response = await api.post<AuthResult | SuccessEnvelope<AuthResult>>(
      "/api/v1/auth/verify-otp",
      { mobile_number: phone, otp_code: code },
    );
    const payload =
      "data" in response
        ? response.data
        : response;

    if (!payload || !payload.access_token) {
      throw new Error("Authentication succeeded without an access token.");
    }

    localStorage.setItem("access_token", payload.access_token);
    if (payload.refresh_token) {
      localStorage.setItem("refresh_token", payload.refresh_token);
    }
    window.location.href = "/";
  }

  return (
    <main className="mx-auto flex min-h-screen max-w-lg items-center justify-center p-6">
      {step === "login" ? (
        <LoginForm onLogin={requestOtp} />
      ) : (
        <div className="w-full">
          <button
            type="button"
            onClick={() => setStep("login")}
            className="mb-4 text-sm text-blue-600 hover:underline"
          >
            ← تغییر شماره
          </button>
          <OtpVerifyForm phoneNumber={phoneNumber} onVerify={verifyOtp} />
        </div>
      )}
    </main>
  );
}
