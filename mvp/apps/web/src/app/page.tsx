import Image from "next/image";
import Link from "next/link";

const flowSteps = [
  {
    number: "01",
    label: "کشف",
    title: "بازار را سریع‌تر پیدا کن",
    body: "کالایی که می‌خواهی را پیدا کن و از بین گزینه‌ها راحت انتخاب کن؛ دیگر لازم نیست برای هر قلم چند جا سر بزنی.",
  },
  {
    number: "02",
    label: "سبد",
    title: "یک سبد، چند بنکدار",
    body: "همه خریدت را یکجا جمع کن؛ پُل سفارش را بین بنکدارها تقسیم می‌کند و نتیجه را یکجا به تو نشان می‌دهد.",
  },
  {
    number: "03",
    label: "سفارش",
    title: "از ثبت سفارش تا پیگیری",
    body: "سفارش را ثبت کن، وضعیتش را ببین و تا رسیدنش به فروشگاه از مرحله بعد باخبر باش.",
  },
  {
    number: "04",
    label: "شفافیت",
    title: "آخرش هم می‌دانی چه شد",
    body: "وضعیت پرداخت، فاکتور و پیگیری‌های لازم در همان مسیر می‌ماند؛ چیزی گم نمی‌شود.",
  },
];

const brandAssets = {
  corporate: "/brand/corporate",
  market: "/brand/market",
  vendor: "/brand/vendor",
} as const;

const roleCards = [
  {
    eyebrow: "برای خرده‌فروشان",
    title: "خرید عمده، راحت‌تر",
    body: "کالا را پیدا کن، قیمت و موجودی را ببین، سبدت را ببند و سفارش بده.",
    href: "/retailer",
    cta: "ورود به بازار",
    logo: brandAssets.market,
    logoAlt: "پل مغازه‌دار",
  },
  {
    eyebrow: "برای تأمین‌کنندگان",
    title: "فروش را یکجا جمع کن",
    body: "کالا، قیمت، موجودی و سفارش‌ها را از یک جا مدیریت کن و ببین چه چیزی منتظر اقدام توست.",
    href: "/vendor",
    cta: "ورود به پنل",
    logo: brandAssets.vendor,
    logoAlt: "پل بنکدار",
  },
  {
    eyebrow: "برای تیم عملیات",
    title: "حواست به کارهای مهم باشد",
    body: "کارهای عقب‌مانده، پشتیبانی و پیگیری سفارش‌ها را یکجا ببین و سریع‌تر جمعشان کن.",
    href: "/ops",
    cta: "ورود به عملیات",
    logo: brandAssets.corporate,
    logoAlt: "پُــــل",
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
          <Link href="/" className="pol-brand" aria-label="پُــــل">
            <Image
              className="pol-brand-logo"
              src={brandAssets.corporate}
              alt="پُــــل"
              width={132}
              height={44}
              priority
              unoptimized
            />
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
            <details className="pol-mobile-menu">
              <summary aria-label="باز کردن منو">
                <span />
                <span />
                <span />
              </summary>
              <nav aria-label="منوی موبایل">
                <Link href="/how">چگونه کار می‌کند</Link>
                <Link href="/retailers">خرده‌فروشان</Link>
                <Link href="/vendors">تأمین‌کنندگان</Link>
                <Link href="/pilot">پایلوت اهواز</Link>
              </nav>
            </details>
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
                <span>تجارت عمده</span>
                <span className="pol-kicker-separator">·</span>
                <span>پایلوت اهواز</span>
              </div>

              <h1>
                خرید عمده،<span className="pol-gradient-text"> یک مسیر روشن.</span>
              </h1>

              <p className="pol-hero-lead">
                پُل فروشگاه‌ها را به بنکدارها و تأمین‌کننده‌ها وصل می‌کند؛ کالا را پیدا می‌کنی، به سبد می‌زنی، سفارش می‌دهی و وضعیتش را دنبال می‌کنی.
              </p>

              <div className="pol-hero-actions">
                <Link href="/auth/login" className="pol-button pol-button-primary">
                  ورود با شماره موبایل
                  <span aria-hidden="true">←</span>
                </Link>
                <a href="#how-it-works" className="pol-button pol-button-secondary">
                  ببین پُل چطور کار می‌کند
                </Link>
              </div>

              <div className="pol-hero-note">
                <span className="pol-note-line" />
                <span>برای فروشگاه‌ها، بنکدارها و تیم پُل</span>
              </div>
            </div>

            <div className="pol-hero-visual pol-reveal pol-delay-2" role="img" aria-label="نمایش جریان سفارش در پُل">
              <div className="pol-visual-grid" />
              <div className="pol-visual-halo" />

              <div className="pol-network-line pol-network-line-a" />
              <div className="pol-network-line pol-network-line-b" />
              <div className="pol-network-line pol-network-line-c" />

              <div className="pol-node pol-node-a">
                <span className="pol-node-dot" />
                <span>فروشگاه</span>
                <strong>سبد</strong>
              </div>

              <div className="pol-node pol-node-b">
                <span className="pol-node-dot" />
                <span>تقسیم سفارش</span>
                <strong>تخصیص</strong>
              </div>

              <div className="pol-node pol-node-c">
                <span className="pol-node-dot" />
                <span>بنکدار</span>
                <strong>سفارش</strong>
              </div>

              <div className="pol-flow-core">
                <div className="pol-core-ring pol-core-ring-one" />
                <div className="pol-core-ring pol-core-ring-two" />
                <div className="pol-core-mark">
                  <Image
                    className="pol-core-logo"
                    src={brandAssets.corporate}
                    alt="پُــــل"
                    width={112}
                    height={48}
                    unoptimized
                  />
                </div>
                <div className="pol-core-caption">B2B COMMERCE</div>
              </div>

              <div className="pol-floating-card pol-floating-card-top">
                <span>موجودی</span>
                <strong>همین حالا قابل مشاهده</strong>
              </div>

              <div className="pol-floating-card pol-floating-card-bottom">
                <span>سفارش‌های تو</span>
                <strong>یک سبد · چند بنکدار</strong>
              </div>
            </div>
          </div>

          <div className="pol-container pol-hero-rail">
            <div>
              <span>یک سبد</span>
              <strong>چند تأمین‌کننده</strong>
            </div>
            <div>
              <span>یک سفارش</span>
              <strong>از ثبت تا تحویل</strong>
            </div>
            <div>
              <span>یک سابقه</span>
              <strong>برای پیگیری خرید</strong>
            </div>
          </div>
        </section>

        <section id="how-it-works" className="pol-section pol-section-soft">
          <div className="pol-container">
            <div className="pol-section-heading pol-reveal">
              <div>
                <span className="pol-overline">پُل چطور کار می‌کند؟</span>
                <h2>از پیدا کردن کالا تا رسیدنش به دستت.</h2>
              </div>
              <p>
                همه‌چیز در یک مسیر جمع می‌شود؛ از انتخاب کالا و بستن سبد تا ثبت سفارش و پیگیری تحویل.
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
              <span className="pol-overline">ONE NETWORK, THREE ROLES</span>
              <h2>هر نقش، همان تراکنش؛ با نمای درست خودش.</h2>
              <p>
                پُل برای سه نقش اصلی، یک مسیر مشترک می‌سازد و نمایش را متناسب با مسئولیت هر نقش نگه می‌دارد.
              </p>
            </div>

            <div className="pol-role-grid">
              {roleCards.map((card, index) => (
                <article
                  key={card.title}
                  className={index === 1 ? "pol-role-card pol-role-card-featured" : "pol-role-card"}
                >
                  <div className="pol-role-brand-wrap">
                    <Image
                      className="pol-role-logo"
                      src={card.logo}
                      alt={card.logoAlt}
                      width={172}
                      height={64}
                      unoptimized
                    />
                    <span className="pol-role-icon" aria-hidden="true">
                      {index === 0 ? "↗" : index === 1 ? "◈" : "◎"}
                    </span>
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
              <h2>پُل فقط ویترین نیست؛ جریان سفارش را به هم وصل می‌کند.</h2>
              <p>
                پُل فقط یک ویترین آنلاین نیست. موجودی، سفارش، پذیرش و تحویل در همان مسیر دیده می‌شوند تا هر نقش، تصویر
                واضح‌تری از اتفاق بعدی داشته باشد.
              </p>

              <div className="pol-metric-row">
                <div>
                  <strong>01</strong>
                  <span>یک سبد چندفروشنده‌ای</span>
                </div>
                <div>
                  <strong>02</strong>
                  <span>چند بنکدار در یک سبد</span>
                </div>
                <div>
                  <strong>03</strong>
                  <span>پیگیری تا رسیدن سفارش</span>
                </div>
              </div>
            </div>

            <div className="pol-command-card pol-reveal pol-delay-2">
              <div className="pol-command-header">
                <div>
                  <span>LIVE ORDER FLOW</span>
                  <strong>جریان واقعی سفارش</strong>
                </div>
                <span className="pol-live-badge">در حال انجام</span>
              </div>

              <div className="pol-command-flow">
                <div className="pol-command-step is-done">
                  <span>۱</span>
                  <div>
                    <strong>سبد خرید</strong>
                    <small>۳ قلم</small>
                  </div>
                </div>
                <div className="pol-command-arrow">↓</div>
                <div className="pol-command-step is-active">
                  <span>۲</span>
                  <div>
                    <strong>تخصیص سفارش</strong>
                    <small>۲ تأمین‌کننده</small>
                  </div>
                </div>
                <div className="pol-command-arrow">↓</div>
                <div className="pol-command-step">
                  <span>۳</span>
                  <div>
                    <strong>ارسال و پیگیری</strong>
                    <small>قابل پیگیری</small>
                  </div>
                </div>
              </div>

              <div className="pol-command-footer">
                <span>سابقه سفارش</span>
                <strong>ثبت‌شده</strong>
              </div>
            </div>
          </div>
        </section>

        <section className="pol-cta-section" id="pilot">
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
                بیشتر درباره پُل و پایلوت اهواز
              </Link>
            </div>
          </div>
        </section>
      </main>

      <footer className="pol-footer">
        <div className="pol-container pol-footer-inner">
          <div className="pol-footer-brand">
            <Image
              className="pol-footer-logo"
              src={brandAssets.corporate}
              alt="پُــــل"
              width={120}
              height={40}
              unoptimized
            />
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
