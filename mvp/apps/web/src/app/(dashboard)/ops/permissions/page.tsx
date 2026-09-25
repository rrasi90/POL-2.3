"use client";

import { useEffect, useState } from "react";
import { ErrorState, Skeleton } from "@pol/ui";
import { getApi } from "@/lib/auth/api";
import { cardCls, type LoadState } from "../../_shared";

interface PermissionData { roles?: Record<string,string[]>; source?: string; }

export default function OpsPermissionsPage() {
  const [data,setData]=useState<PermissionData|null>(null);
  const [state,setState]=useState<LoadState>("loading");
  const [error,setError]=useState<string|null>(null);

  useEffect(()=>{void (async()=>{
    try {
      const value=await getApi().get<PermissionData>("/api/v1/ops/permissions");
      setData(value); setState("ready");
    } catch(e) { setError(e instanceof Error?e.message:"دریافت مجوزها ناموفق بود"); setState("error"); }
  })()},[]);

  if(state==="loading") return <div className="space-y-4" aria-busy="true"><Skeleton className="h-8 w-48"/><div className={cardCls}><Skeleton lines={10}/></div></div>;
  if(state==="error") return <ErrorState title="دریافت مجوزها ناموفق بود" description={error??undefined}/>;

  return <div className="space-y-4">
    <header><h1 className="text-[24px] font-bold text-[var(--pol-light-text-primary)]">کاتالوگ مجوزها</h1><p className="mt-1 text-[12px] text-[var(--pol-light-text-muted)]">OP-11 · مرجع مجوزهای کانونیکال</p></header>
    {data?.roles ? Object.entries(data.roles).map(([role,permissions])=>
      <section key={role} className={cardCls}>
        <div className="flex flex-wrap items-center gap-2"><h2 className="font-semibold text-[var(--pol-light-text-primary)]">{role}</h2><span className="text-[11px] text-[var(--pol-light-text-muted)]">{permissions.length.toLocaleString("fa-IR")} مجوز</span></div>
        <div className="mt-3 flex flex-wrap gap-2">{permissions.map(p=><span key={p} className="rounded-full border border-[var(--pol-light-border-subtle)] px-2.5 py-1 text-[12px] text-[var(--pol-light-text-secondary)]">{p}</span>)}</div>
      </section>
    ):null}
    <p className="text-[11px] text-[var(--pol-light-text-muted)]">{data?.source ?? ""}</p>
  </div>;
}
