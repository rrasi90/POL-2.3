"use client";

import { EmptyState, StatusChip, Button, SearchField, Skeleton, ErrorState } from "@pol/ui";

export default function ComponentDemoPage() {
  return (
    <main className="mx-auto max-w-4xl space-y-8 p-6">
      <header>
        <h1 className="text-[24px] leading-[32px] font-bold">Golden Components — Phase 1</h1>
        <p className="text-[13px] text-[var(--pol-light-text-secondary)]">
          doc 39 contracts · doc 21 §16 states · doc 56 tokens
        </p>
      </header>

      <section className="space-y-3">
        <h2 className="text-[16px] font-semibold">Button</h2>
        <div className="flex flex-wrap gap-2">
          <Button>primary</Button>
          <Button variant="secondary">secondary</Button>
          <Button variant="ghost">ghost</Button>
          <Button variant="danger">danger</Button>
          <Button variant="success">success</Button>
          <Button loading>loading</Button>
          <Button disabled>disabled</Button>
          <Button size="sm">sm</Button>
          <Button size="lg">lg</Button>
        </div>
      </section>

      <section className="grid gap-4 sm:grid-cols-2">
        <label className="block text-[12px]">
          Search
          <SearchField placeholder="جستجوی کالا…" className="mt-1" />
        </label>
        <div className="space-y-2">
          <StatusChip tone="success">موجود</StatusChip>{" "}
          <StatusChip tone="warning">کم</StatusChip>{" "}
          <StatusChip tone="danger">ناموجود</StatusChip>{" "}
          <StatusChip tone="info">در انتظار</StatusChip>{" "}
          <StatusChip>خنثی</StatusChip>
        </div>
      </section>

      <section className="space-y-3">
        <h2 className="text-[16px] font-semibold">States</h2>
        <Skeleton lines={3} />
        <EmptyState
          title="موردی یافت نشد"
          description="فیلترها را تغییر دهید یا عبارت دیگری جستجو کنید."
          actionLabel="پاک کردن فیلترها"
          onAction={() => undefined}
        />
        <ErrorState description="اتصال به سرور برقرار نشد." onRetry={() => undefined} />
      </section>
    </main>
  );
}
