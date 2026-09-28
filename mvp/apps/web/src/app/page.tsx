import Link from "next/link";

const flowSteps = [
  {
    number: "01",
    label: "کشف",
    title: "بازار را سریع‌تر پیدا کن",
    body: "کالا و تأمین‌کننده را در یک فضای B2B منظم ببین؛ بدون اینکه سفارش‌گیری از چند منبع تبدیل به چند مسیر جداگانه شود.",
  },
  {
    number: "02",
    label: "سبد",
    title: "یک سبد، چند تأمین‌کننده",
    body: "سبد چندفروشنده‌ای اقلام را جمع می‌کند و موتور تخصیص، سفارش‌ها را بر اساس ظرفیت و قواعد هر تأمین‌کننده تفکیک می‌کند.",
  },
  {
    number: "03",
    label: "سفارش",
    title: "از checkout تا پیگیری",
    body: "ثبت سفارش، پذیرش، fulfillment و وضعیت تحویل در یک زنجیره قابل‌ردگیری ادامه پیدا می‌کند.",
  },
  {
    number: "04",
    label: "شفافیت",
    title: "تسویه و اختلاف، قابل مشاهده",
    body: "رویدادهای مالی، شواهد و مغایرت‌ها در همان جریان عملیاتی ثبت و پیگیری می‌شوند.",
  },
];

const roleCards = [
  {
    eyebrow: "برای خرده‌فروشان",
    title: "خرید عمده، بدون اصطکاک اضافه",
    body: "کاتالوگ، موجودی، سبد و سفارش را در یک مسیر واحد مدیریت کن.",
    href: "/retailer",
    cta: "ورود به بازار",
  },
  {
    eyebrow: "برای تأمین‌کنندگان",
    title: "فروش و عملیات را یکجا ببین",
    body: "کاتالوگ، قیمت، موجودی، پذیرش سفارش و fulfillment را از یک نقطه کنترل کن.",
    href: "/vendor",
    cta: "ورود به پنل",
  },
  {
    eyebrow: "برای تیم عملیات",
    title: "استثناها را به‌موقع ببین",
    body: "صف‌ها، پشتیبانی، reconciliation و audit را بر مبنای وضعیت واقعی عملیات دنبال کن.",
    href: "/ops",
    cta: "ورود به عملیات",
  },
];

function FlowCard({
  step,
}: {
  step: (typeof flowSteps)[number];
}) {
  return (
    <article className="pol-flow-card">
      <div className="pol-flow-card-top">
        <span className="pol-index">{step.number}</span>
        <span className="pol-chip">{step.label}</span>
      </div>
      <h3>{step.title}</h3>
      <p>{step.body}</p>
    </article>
  );
}

export default function HomePage() {
  return (
    <div className="pol-landing">
      <header className="pol-nav">
        <div className="pol-container pol-nav-inner">
          <Link href="/" className="pol-brand" aria-label="پُل">
            <span className="pol-brand-mark">پُ</span>
            <span className="pol-brand-word">پُــــل</span>
          </Link>

          <nav className="pol-nav-links" aria-label="ناوبری اصلی">
            <Link href="/how">چگونه کار می‌کند</Link>
            <Link href="/retailers">خرده‌فروشان</Link>
            <Link href="/vendors">تأمین‌کنندگان</Link>
            <Link href="/pilot">پایلوت اهواز</Link>
          </nav>

          <div className="pol-nav-actions">
            <Link href="/auth/login" className="pol-text-link">
              ورود
            </Link>
            <Link href="/auth/login" className="pol-button pol-button-primary pol-button-small">
              شروع با شماره موبایل
            </Link>
          </div>
        </div>
      </header>

      <main>
        <section className="pol-hero">
          <div className="pol-hero-orb pol-hero-orb-one" />
          <div className="pol-hero-orb pol-hero-orb-two" />

          <div className="pol-container pol-hero-grid">
            <div className="pol-hero-copy pol-reveal">
              <div className="pol-kicker">
                <span className="pol-status-dot" />
                <span>PRECISION COMMERCE</span>
                <span className="pol-kicker-separator">·</span>
                <span>پایلوت فعال اهواز</span>
              </div>

              <h1>
                تجارت عمده را
                <span className="pol-gradient-text"> یک مسیر دقیق‌تر</span>
                کن.
              </h1>

              <p className="pol-hero-lead">
                پُل، لایه عملیاتی تجارت B2B است؛ جایی که خرده‌فروش، تأمین‌کننده
                و عملیات، از کشف کالا تا سفارش، fulfillment و پیگیری را در یک
                جریان منسجم می‌بینند.
              </p>

              <div className="pol-hero-actions">
                <Link href="/auth/login" className="pol-button pol-button-primary">
                  ورود با شماره موبایل
                  <span aria-hidden="true">←</span>
                </Link>
                <Link href="/how" className="pol-button pol-button-secondary">
                  ببین پُل چگونه کار می‌کند
                </Link>
              </div>

              <div className="pol-hero-note">
                <span className="pol-note-line" />
                <span>ساخته‌شده برای workflow واقعی بنکداری B2B</span>
              </div>
            </div>

            <div className="pol-hero-visual pol-reveal pol-delay-2" aria-label="نمایش جریان سفارش در پُل">
              <div className="pol-visual-grid" />
              <div className="pol-visual-halo" />

              <div className="pol-network-line pol-network-line-a" />
              <div className="pol-network-line pol-network-line-b" />
              <div className="pol-network-line pol-network-line-c" />

              <div className="pol-node pol-node-a">
                <span className="pol-node-dot" />
                <span>Retailer</span>
                <strong>سبد</strong>
              </div>

              <div className="pol-node pol-node-b">
                <span className="pol-node-dot" />
                <span>Allocation</span>
                <strong>تخصیص</strong>
              </div>

              <div className="pol-node pol-node-c">
                <span className="pol-node-dot" />
                <span>Vendor</span>
                <strong>سفارش</strong>
              </div>

              <div className="pol-flow-core">
                <div className="pol-core-ring pol-core-ring-one" />
                <div className="pol-core-ring pol-core-ring-two" />
                <div className="pol-core-mark">پُ</div>
                <div className="pol-core-caption">POL</div>
              </div>

              <div className="pol-floating-card pol-floating-card-top">
                <span>موجودی</span>
                <strong>همین حالا قابل مشاهده</strong>
              </div>

              <div className="pol-floating-card pol-floating-card-bottom">
                <span>OrderGroup</span>
                <strong>یک سفارش · چند جریان</strong>
              </div>
            </div>
          </div>

          <div className="pol-container pol-hero-rail">
            <div>
              <span>یک سبد</span>
              <strong>چند تأمین‌کننده</strong>
            </div>
            <div>
              <span>یک جریان</span>
              <strong>از سفارش تا تحویل</strong>
            </div>
            <div>
              <span>یک سابقه</span>
              <strong>برای عملیات و audit</strong>
            </div>
          </div>
        </section>

        <section className="pol-section pol-section-soft">
          <div className="pol-container">
            <div className="pol-section-heading pol-reveal">
              <div>
                <span className="pol-overline">HOW POL WORKS</span>
                <h2>از کشف تا تسویه، مسیر را کوتاه‌تر کن.</h2>
              </div>
              <p>
                معماری پُل برای حذف پراکندگی طراحی شده است: یک سبد، یک checkout،
                چند سفارش قابل‌تفکیک و یک زنجیره قابل‌پیگیری.
              </p>
            </div>

            <div className="pol-flow-grid">
              {flowSteps.map((step, index) => (
                <div
                  key={step.number}
                  className={index % 2 === 0 ? "pol-reveal" : "pol-reveal pol-delay-1"}
                >
                  <FlowCard step={step} />
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="pol-section">
          <div className="pol-container">
            <div className="pol-section-heading pol-section-heading-centered pol-reveal">
              <span className="pol-overline">ONE NETWORK, THREE PERSPECTIVES</span>
              <h2>هر نقش، همان تراکنش؛ با نمای درست خودش.</h2>
              <p>
                پُل برای سه طرف اصلی workflow، یک زبان مشترک می‌سازد و نمایش را
                متناسب با مسئولیت هر نقش نگه می‌دارد.
              </p>
            </div>

            <div className="pol-role-grid">
              {roleCards.map((card, index) => (
                <article
                  key={card.title}
                  className={index === 1 ? "pol-role-card pol-role-card-featured" : "pol-role-card"}
                >
                  <div className="pol-role-icon" aria-hidden="true">
                    {index === 0 ? "↗" : index === 1 ? "◈" : "◎"}
                  </div>
                  <span className="pol-overline">{card.eyebrow}</span>
                  <h3>{card.title}</h3>
                  <p>{card.body}</p>
                  <Link href={card.href} className="pol-inline-link">
                    {card.cta}
                    <span aria-hidden="true">←</span>
                  </Link>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section className="pol-section pol-precision-section">
          <div className="pol-container pol-precision-grid">
            <div className="pol-precision-copy pol-reveal">
              <span className="pol-overline">PRECISION COMMERCE</span>
              <h2>اطلاعات خوب، وقتی ارزش دارد که وارد تصمیم روزانه شود.</h2>
              <p>
                پُل فقط storefront نیست. داده سفارش، موجودی، پذیرش، تحویل،
                settlement و dispute را در همان جریان عملیاتی نگه می‌دارد تا تیم
                بتواند براساس واقعیت تصمیم بگیرد.
              </p>

              <div className="pol-metric-row">
                <div>
                  <strong>01</strong>
                  <span>یک سبد چندفروشنده‌ای</span>
                </div>
                <div>
                  <strong>02</strong>
                  <span>تخصیص deterministic</span>
                </div>
                <div>
                  <strong>03</strong>
                  <span>رهگیری تا fulfillment</span>
                </div>
              </div>
            </div>

            <div className="pol-command-card pol-reveal pol-delay-2">
              <div className="pol-command-header">
                <div>
                  <span>LIVE FLOW</span>
                  <strong>Order orchestration</strong>
                </div>
                <span className="pol-live-badge">ONLINE</span>
              </div>

              <div className="pol-command-flow">
                <div className="pol-command-step is-done">
                  <span>۱</span>
                  <div>
                    <strong>Basket</strong>
                    <small>۳ قلم</small>
                  </div>
                </div>
                <div className="pol-command-arrow">↓</div>
                <div className="pol-command-step is-active">
                  <span>۲</span>
                  <div>
                    <strong>AllocationPlan</strong>
                    <small>۲ Vendor</small>
                  </div>
                </div>
                <div className="pol-command-arrow">↓</div>
                <div className="pol-command-step">
                  <span>۳</span>
                  <div>
                    <strong>OrderGroup</strong>
                    <small>قابل پیگیری</small>
                  </div>
                </div>
              </div>

              <div className="pol-command-footer">
                <span>Idempotency</span>
                <strong>فعال</strong>
              </div>
            </div>
          </div>
        </section>

        <section className="pol-cta-section">
          <div className="pol-container pol-cta-card pol-reveal">
            <div>
              <span className="pol-overline">AHVAZ PILOT</span>
              <h2>پُل را در جریان واقعی سفارش ببین.</h2>
              <p>
                از ورود با شماره موبایل شروع کن و مسیر کشف، سبد و سفارش را
                تجربه کن.
              </p>
            </div>
            <div className="pol-cta-actions">
              <Link href="/auth/login" className="pol-button pol-button-light">
                ورود به سامانه
                <span aria-hidden="true">←</span>
              </Link>
              <Link href="/pilot" className="pol-cta-secondary">
                درباره پایلوت اهواز
              </Link>
            </div>
          </div>
        </section>
      </main>

      <footer className="pol-footer">
        <div className="pol-container pol-footer-inner">
          <div className="pol-footer-brand">
            <span className="pol-brand-mark">پُ</span>
            <div>
              <strong>پُــــل</strong>
              <span>زیرساخت سفارش‌گذاری B2B</span>
            </div>
          </div>

          <nav aria-label="پیوندهای فوتر" className="pol-footer-links">
            <Link href="/about">درباره ما</Link>
            <Link href="/how">چگونه کار می‌کند</Link>
            <Link href="/retailers">خرده‌فروشان</Link>
            <Link href="/vendors">تأمین‌کنندگان</Link>
            <Link href="/contact">تماس</Link>
          </nav>

          <span className="pol-footer-meta">© 2026 POL</span>
        </div>
      </footer>
    </div>
  );
}
