"use client";

import Link from "next/link";

export default function HomePage() {
  return (
    <main className="mx-auto flex min-h-screen max-w-4xl items-center justify-center p-6">
      <section className="w-full rounded-2xl border border-gray-200 bg-white p-8 shadow-sm">
        <p className="mb-2 text-sm font-medium text-blue-600">پُل / POL</p>
        <h1 className="text-3xl font-bold">B2B FMCG Platform</h1>
        <p className="mt-3 max-w-2xl text-gray-600">
          Frontend foundation wired to the canonical POL API contracts.
        </p>
        <div className="mt-6">
          <Link
            href="/auth"
            className="inline-flex rounded-lg bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700"
          >
            ورود
          </Link>
        </div>
      </section>
    </main>
  );
}
