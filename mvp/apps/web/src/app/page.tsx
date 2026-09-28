import Image from "next/image";
import Link from "next/link";

const flowSteps = [
  {
    number: "۰۱",
    label: "پیدا کن",
    title: "کالای موردنیازت را پیدا کن",
    body: "کالا را ببین، قیمت و موجودی را مقایسه کن و بدون تماس‌های پراکنده انتخابت را انجام بده.",
  },
  {
    number: "۰۲",
    label: "سبد",
    title: "همه خریدت در یک سبد",
    body: "چند قلم از چند بنکدار را کنار هم بگذار؛ پُل سفارش را بین آن‌ها مرتب می‌کند.",
  },
  {
    number: "۰۳",
    label: "سفارش",
    title: "سفارش بده و وضعیتش را ببین",
    body: "ثبت سفارش تا آماده‌سازی و تحویل را مرحله‌به‌مرحله دنبال کن.",
  },
  {
    number: "۰۴",
    label: "پیگیری",
    title: "بدان سفارش کجاست",
    body: "وضعیت پرداخت، فاکتور و پیگیری سفارش‌ها همان‌جا در دسترس توست.",
  },
];

const brandAssets = {
  corporate: "/brand/corporate",
  market: "/brand/market",
  vendor: "/brand/vendor",
} as const;

const roleCards = [
  {
    id: "retailers",
    eyebrow: "برای فروشگاه‌ها",
    title: "خرید عمده، راحت‌تر",
    body: "کالا را پیدا کن، قیمت و موجودی را ببین، سبدت را ببند و سفارش بده.",
    href: "/retailer",
    cta: "ورود به بازار",
    logo: brandAssets.market,
    logoAlt: "پُــــل برای فروشگاه‌ها",
  },
  {
    id: "vendors",
    eyebrow: "برای بنکدارها",
    title: "فروش را یکجا جمع کن",
    body: "کالا، قیمت، موجودی و سفارش‌ها را از یک جا مدیریت کن و بدان چه کاری باید انجام شود.",
    href: "/vendor",
    cta: "ورود به پنل",
    logo: brandAssets.vendor,
    logoAlt: "پُــــل برای بنکدارها",
  },
  {
    id: "operations",
    eyebrow: "برای تیم پُل",
    title: "کارهای مهم را یکجا ببین",
    body: "پیگیری سفارش‌ها، پشتیبانی و موارد نیازمند اقدام را از یک جا دنبال کن.",
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
    <div className="pol-landing" dir="rtl">
      <header className="pol-nav">
        <div className="pol-container pol-nav-inner">
          <a href="#top" className="pol-brand" aria-label="رفتن به ابتدای پُــــل">
            <Image
              className="pol-brand-logo"
              src={brandAssets.corporate}
              alt="پُــــل"
              width={132}
              height={44}
              priority
              unoptimized
            />
          </a>

          <nav className="pol-nav-links" aria-label="ناوبری اصلی">
            <a href="#how-it-works">چطور کار می‌کند</a>
            <a href="#retailers">برای فروشگاه‌ها</a>
            <a href="#vendors">برای بنکدارها</a>
            <a href="#pilot">پایلوت اهواز</a>
          </nav>

          <div className="pol-nav-actions">
            <Link href="/auth/login" className="pol-text-link">
              ورود
            </Link>
            <Link href="/auth/login" className="pol-button pol-button-primary pol-button-small">
              شروع با شماره موبایل
            </Link>
            <details className="pol-mobile-menu">
              <summary aria-label="باز کردن منوی پُــــل">
                <span />
                <span />
                <span />
              </summary>
              <nav aria-label="منوی موبایل">
                <a href="#how-it-works">چطور کار می‌کند</a>
                <a href="#retailers">برای فروشگاه‌ها</a>
                <a href="#vendors">برای بنکدارها</a>
                <a href="#pilot">پایلوت اهواز</a>
              </nav>
            </details>
          </div>
        </div>
      </header>

      <main id="top">
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
                خرید عمده<span className="pol-gradient-text">، ساده‌تر از همیشه.</span>
              </h1>

              <p className="pol-hero-lead">
                پُل فروشگاه‌ها را به بنکدارها و تأمین‌کننده‌ها وصل می‌کند؛
                کالا را پیدا می‌کنی، به سبد می‌زنی، سفارش می‌دهی و وضعیتش را
                دنبال می‌کنی.
              </p>

              <div className="pol-hero-actions">
                <Link href="/auth/login" className="pol-button pol-button-primary">
                  شروع خرید
                  <span aria-hidden="true">←</span>
                </Link>
                <a href="#how-it-works" className="pol-button pol-button-secondary">
                  ببین چطور کار می‌کند
                </a>
              </div>

              <div className="pol-hero-note">
                <span className="pol-note-line" />
                <span>برای فروشگاه‌ها، بنکدارها و تیم پُل</span>
              </div>
            </div>

            <div
              className="pol-hero-visual pol-reveal pol-delay-2"
              role="img"
              aria-label="نمایش مسیر سفارش از فروشگاه تا بنکدار"
            >
              <div className="pol-visual-grid" />
              <div className="pol-visual-halo" />

              <div className="pol-network-line pol-network-line-a" />
              <div className="pol-network-line pol-network-line-b" />
              <div className="pol-network-line pol-network-line-c" />

              <div className="pol-node pol-node-a">
                <span className="pol-node-dot" />
                <span>فروشگاه</span>
                <strong>سبد خرید</strong>
              </div>

              <div className="pol-node pol-node-b">
                <span className="pol-node-dot" />
                <span>پُل</span>
                <strong>مرتب‌سازی سفارش</strong>
              </div>

              <div className="pol-node pol-node-c">
                <span className="pol-node-dot" />
                <span>بنکدار</span>
                <strong>آماده‌سازی</strong>
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
                <div className="pol-core-caption">تجارت عمده</div>
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
              <strong>چند بنکدار</strong>
            </div>
            <div>
              <span>یک مسیر</span>
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
                <h2>از پیدا کردن کالا تا رسیدنش به فروشگاه</h2>
              </div>
              <p>
                همه‌چیز در یک مسیر جمع می‌شود؛ انتخاب کالا، بستن سبد، ثبت سفارش
                و پیگیری تحویل.
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

        <section id="roles" className="pol-section">
          <div className="pol-container">
            <div className="pol-section-heading pol-section-heading-centered pol-reveal">
              <span className="pol-overline">یک پُل برای همه</span>
              <h2>هرکس، کار خودش را ساده‌تر انجام می‌دهد.</h2>
              <p>
                فروشگاه، بنکدار و تیم پُل هرکدام همان سفارش را از زاویه خودشان
                می‌بینند.
              </p>
            </div>

            <div className="pol-role-grid">
              {roleCards.map((card, index) => (
                <article
                  key={card.id}
                  id={card.id}
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
              <span className="pol-overline">چرا پُل؟</span>
              <h2>خرید و فروش عمده را به هم وصل می‌کنیم.</h2>
              <p>
                کالا، موجودی، سفارش و تحویل در یک مسیر دیده می‌شوند؛ لازم نیست
                برای فهمیدن وضعیت سفارش بین چند ابزار جابه‌جا شوی.
              </p>

              <div className="pol-metric-row">
                <div>
                  <strong>۰۱</strong>
                  <span>یک سبد، چند بنکدار</span>
                </div>
                <div>
                  <strong>۰۲</strong>
                  <span>یک مسیر برای سفارش</span>
                </div>
                <div>
                  <strong>۰۳</strong>
                  <span>پیگیری تا رسیدن سفارش</span>
                </div>
              </div>
            </div>

            <div className="pol-command-card pol-reveal pol-delay-2">
              <div className="pol-command-header">
                <div>
                  <span>مسیر سفارش</span>
                  <strong>همین سفارشی که ثبت کردی</strong>
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
                    <strong>مرتب‌سازی سفارش</strong>
                    <small>۲ بنکدار</small>
                  </div>
                </div>
                <div className="pol-command-arrow">↓</div>
                <div className="pol-command-step">
                  <span>۳</span>
                  <div>
                    <strong>ارسال و تحویل</strong>
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
              <span className="pol-overline">پایلوت اهواز</span>
              <h2>خریدت را همین‌جا شروع کن.</h2>
              <p>با شماره موبایل وارد شو و خرید عمده را شروع کن.</p>
            </div>
            <div className="pol-cta-actions">
              <Link href="/auth/login" className="pol-button pol-button-light">
                ورود به پُل
                <span aria-hidden="true">←</span>
              </Link>
              <Link href="/pilot" className="pol-cta-secondary">
                بیشتر درباره پُل
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
              <span>بازار و سفارش عمده</span>
            </div>
          </div>

          <nav aria-label="پیوندهای فوتر" className="pol-footer-links">
            <a href="#how-it-works">چطور کار می‌کند</a>
            <a href="#retailers">برای فروشگاه‌ها</a>
            <a href="#vendors">برای بنکدارها</a>
            <a href="#pilot">پایلوت اهواز</a>
            <Link href="/contact">تماس با ما</Link>
          </nav>

          <span className="pol-footer-meta">© ۲۰۲۶ پُــــل</span>
        </div>
      </footer>
    </div>
  );
}
