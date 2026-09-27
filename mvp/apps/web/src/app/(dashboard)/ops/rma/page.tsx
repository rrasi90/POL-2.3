"use client";

import { useCallback, useEffect, useState } from "react";
import { Button, EmptyState, ErrorState, Skeleton, StatusChip } from "@pol/ui";
import { getApi } from "@/lib/auth/api";
import { cardCls, formatDateTime, formatToman, itemsOf, type LoadState } from "../_shared";

interface ReturnRow {
  return_id:string; order_id:string; order_number?:string; status?:string;
  reason?:string; claimed_refund_amount_toman?:number|string|null;
  approved_refund_amount_toman?:number|string|null; retailer_name?:string; vendor_name?:string;
  created_at?:string;
}

export default function OpsRmaPage() {
  const [rows,setRows]=useState<ReturnRow[]>([]);
  const [state,setState]=useState<LoadState>("loading");
  const [error,setError]=useState<string|null>(null);

  const load=useCallback(async()=>{
    setState("loading"); setError(null);
    try {
      const data=await getApi().get<unknown>("/api/v1/ops/returns?limit=50&offset=0");
      setRows(itemsOf<ReturnRow>(data,"returns")); setState("ready");
    } catch(e) { setError(e instanceof Error?e.message:"دریافت پرونده‌های RMA ناموفق بود"); setState("error"); }
  },[]);
  useEffect(()=>{void load()},[load]);

  if(state==="loading") return <div className="space-y-4" aria-busy="true"><Skeleton className="h-8 w-48"/><div className={cardCls}><Skeleton lines={8}/></div></div>;
  if(state==="error") return <ErrorState title="دریافت پرونده‌های RMA ناموفق بود" description={error??undefined} onRetry={()=>void load()}/>;

  return <div className="space-y-4">
    <header className="flex flex-wrap items-baseline gap-3"><h1 className="text-[24px] font-bold text-[var(--pol-light-text-primary)]">RMA و مرجوعی</h1><span className="text-[12px] text-[var(--pol-light-text-muted)]">O-04 · فهرست سراسری</span><Button variant="secondary" size="sm" className="ms-auto" onClick={()=>void load()}>به‌روزرسانی</Button></header>
    {rows.length===0?<EmptyState title="پرونده‌ای وجود ندارد" description="مرجوعی‌های ثبت‌شده از همه سفارش‌ها در این فهرست نمایش داده می‌شوند."/>:
    <ul className="space-y-2">{rows.map(r=><li key={r.return_id} className={cardCls}>
      <div className="flex flex-wrap items-center gap-2"><StatusChip tone={r.status==="APPROVED"?"success":r.status==="REJECTED"?"danger":"warning"}>{r.status??"—"}</StatusChip><span className="font-semibold" dir="ltr">{r.order_number??r.order_id}</span><span className="ms-auto text-[11px] text-[var(--pol-light-text-muted)]">{formatDateTime(r.created_at)}</span></div>
      <div className="mt-2 text-[13px] text-[var(--pol-light-text-secondary)]">{r.retailer_name??"—"} ← {r.vendor_name??"—"}</div>
      <div className="mt-2 text-[12px] text-[var(--pol-light-text-muted)]">{r.reason??"بدون توضیح"}</div>
      <div className="mt-2 flex gap-4 text-[12px]"><span>درخواست: {formatToman(r.claimed_refund_amount_toman)}</span><span>تاییدشده: {formatToman(r.approved_refund_amount_toman)}</span></div>
    </li>)}</ul>}
  </div>;
}
