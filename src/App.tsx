const contractRates = [
  { label: "Month-to-month", value: 42.7 },
  { label: "One year", value: 11.3 },
  { label: "Two year", value: 2.8 },
];

const tenureRates = [
  { label: "0–6 mo", value: 52.9 },
  { label: "7–12", value: 35.9 },
  { label: "13–24", value: 28.7 },
  { label: "25–48", value: 20.4 },
  { label: "49–72", value: 9.5 },
];

const churnDrivers = [
  { label: "Electronic check", value: 45.3 },
  { label: "Fiber optic", value: 41.9 },
  { label: "Senior citizens", value: 41.7 },
  { label: "No tech support", value: 41.6 },
  { label: "Mailed check", value: 19.1 },
  { label: "DSL", value: 19.0 },
  { label: "Bank transfer", value: 16.7 },
  { label: "Credit card", value: 15.2 },
  { label: "With tech support", value: 15.2 },
];

const recommendations = [
  "Move new customers to annual contracts",
  "Add a first-6-months onboarding programme",
  "Bundle tech support and online security",
  "Encourage automatic payment methods",
  "Review fiber optic pricing and service quality",
];

function Footer() {
  return (
    <footer className="frame-footer">
      Source: Telco Customer Churn dataset (Kaggle). Mockup of analysis in FUTURE_DS_02.
    </footer>
  );
}

function FrameHeader({ eyebrow, title }: { eyebrow: string; title: string }) {
  return (
    <header className="frame-header">
      <div>
        <p className="eyebrow">{eyebrow}</p>
        <h1>{title}</h1>
      </div>
      <div className="header-mark" aria-hidden="true">
        <span />
        <span />
        <span />
      </div>
    </header>
  );
}

function KpiCard({
  label,
  value,
  detail,
  tone = "navy",
}: {
  label: string;
  value: string;
  detail?: string;
  tone?: "navy" | "teal" | "red";
}) {
  return (
    <article className={`kpi-card ${tone}`}>
      <p>{label}</p>
      <strong>{value}</strong>
      {detail && <span>{detail}</span>}
    </article>
  );
}

function VerticalBarChart({
  title,
  data,
}: {
  title: string;
  data: { label: string; value: number }[];
}) {
  const max = Math.max(...data.map((item) => item.value));
  return (
    <article className="chart-card">
      <h2>{title}</h2>
      <div className={`vertical-bars ${data.length === 5 ? "five-bars" : ""}`}>
        {data.map((item) => (
          <div className="vertical-bar-item" key={item.label}>
            <div className="vertical-value">{item.value}%</div>
            <div className="bar-track">
              <div className="bar-fill" style={{ height: `${(item.value / max) * 100}%` }} />
            </div>
            <div className="bar-label">{item.label}</div>
          </div>
        ))}
      </div>
    </article>
  );
}

function Overview() {
  return (
    <section className="report-frame">
      <FrameHeader eyebrow="Overview" title="Customer Retention & Churn Overview" />
      <main className="frame-content overview-content">
        <div className="kpi-grid">
          <KpiCard label="Customers" value="7,043" />
          <KpiCard label="Churn rate" value="26.5%" tone="red" />
          <KpiCard label="Churned customers" value="1,869" tone="red" />
          <KpiCard
            label="Monthly revenue lost to churn"
            value="$139K"
            detail="30.5% of $456K"
            tone="red"
          />
          <KpiCard
            label="Avg monthly charge"
            value="$74.44"
            detail="churned vs retained $61.27"
            tone="red"
          />
          <KpiCard
            label="Avg tenure"
            value="18.0"
            detail="churned vs retained 37.6 months"
            tone="teal"
          />
        </div>
        <div className="overview-charts">
          <VerticalBarChart title="Churn rate by contract" data={contractRates} />
          <VerticalBarChart title="Churn rate by tenure" data={tenureRates} />
        </div>
      </main>
      <Footer />
    </section>
  );
}

function ChurnDrivers() {
  const max = churnDrivers[0].value;
  return (
    <section className="report-frame">
      <FrameHeader eyebrow="Churn drivers" title="Factors associated with customer churn" />
      <main className="frame-content drivers-content">
        <article className="drivers-card">
          <div className="section-heading">
            <div>
              <p className="section-kicker">Ranked by churn rate</p>
              <h2>Where churn is concentrated</h2>
            </div>
            <span className="rate-label">Churn rate</span>
          </div>
          <div className="drivers-list">
            {churnDrivers.map((item, index) => (
              <div className="driver-row" key={item.label}>
                <span className="driver-rank">{index + 1}</span>
                <span className="driver-label">{item.label}</span>
                <div className="driver-track">
                  <div
                    className={`driver-fill ${index > 3 ? "muted" : ""}`}
                    style={{ width: `${(item.value / max) * 100}%` }}
                  />
                </div>
                <strong>{item.value.toFixed(1)}%</strong>
              </div>
            ))}
          </div>
          <p className="takeaway">These are factors associated with churn, not proven causes.</p>
        </article>
      </main>
      <Footer />
    </section>
  );
}

const lineSeries = [
  {
    name: "Month-to-month",
    color: "#D1495B",
    points: [
      { x: 0, y: 100, label: "100%" },
      { x: 12, y: 70.3, label: "70.3%" },
      { x: 24, y: 58.6, label: "58.6%" },
      { x: 48, y: 39.7, label: "39.7%" },
    ],
  },
  {
    name: "One year",
    color: "#2A9D8F",
    points: [
      { x: 0, y: 100, label: "100%" },
      { x: 12, y: 99.1, label: "99.1%" },
      { x: 24, y: 97.8, label: "97.8%" },
      { x: 48, y: 91.7, label: "91.7%" },
    ],
  },
  {
    name: "Two year",
    color: "#1F3A5F",
    points: [
      { x: 0, y: 100, label: "100%" },
      { x: 12, y: 100, label: "100%" },
      { x: 24, y: 100, label: "100%" },
      { x: 48, y: 99.6, label: "99.6%" },
    ],
  },
];

const chartX = (month: number) => 84 + (month / 48) * 1000;
const chartY = (value: number) => 46 + ((100 - value) / 70) * 500;

function CustomerLifetime() {
  return (
    <section className="report-frame">
      <FrameHeader eyebrow="Customer lifetime" title="Retention over the customer lifetime" />
      <main className="frame-content lifetime-content">
        <article className="line-chart-card">
          <div className="line-chart-heading">
            <div>
              <p className="section-kicker">Retention curve</p>
              <h2>Share of customers still active</h2>
            </div>
            <div className="legend">
              {lineSeries.map((series) => (
                <span key={series.name}>
                  <i style={{ background: series.color }} />
                  {series.name}
                </span>
              ))}
            </div>
          </div>
          <svg
            className="line-chart"
            viewBox="0 0 1180 650"
            role="img"
            aria-label="Share of customers still active by contract at months 0, 12, 24 and 48"
          >
            <g className="grid-lines">
              <line x1="84" y1="46" x2="1084" y2="46" />
              <line x1="84" y1="296" x2="1084" y2="296" />
              <line x1="84" y1="546" x2="1084" y2="546" />
            </g>
            <line className="axis-line" x1="84" y1="46" x2="84" y2="546" />
            <line className="axis-line" x1="84" y1="546" x2="1084" y2="546" />
            {lineSeries.map((series) => {
              const points = series.points
                .map((point) => `${chartX(point.x)},${chartY(point.y)}`)
                .join(" ");
              return (
                <g key={series.name}>
                  <polyline
                    points={points}
                    fill="none"
                    stroke={series.color}
                    strokeWidth="5"
                    strokeLinejoin="round"
                    strokeLinecap="round"
                  />
                  {series.points.map((point, index) => {
                    const sharedStart = point.x === 0;
                    const labelY =
                      series.name === "Two year"
                        ? chartY(point.y) - 20
                        : series.name === "One year"
                          ? chartY(point.y) + 30
                          : chartY(point.y) - 20;
                    return (
                      <g key={`${series.name}-${point.x}`}>
                        <circle
                          cx={chartX(point.x)}
                          cy={chartY(point.y)}
                          r="7"
                          fill="white"
                          stroke={series.color}
                          strokeWidth="4"
                        />
                        {(!sharedStart || (index === 0 && series.name === "Two year")) && (
                          <text
                            x={chartX(point.x)}
                            y={labelY}
                            textAnchor={point.x === 48 ? "end" : "middle"}
                            fill={series.color}
                          >
                            {point.label}
                          </text>
                        )}
                      </g>
                    );
                  })}
                </g>
              );
            })}
            {[0, 12, 24, 48].map((month) => (
              <g key={month}>
                <line
                  className="tick-line"
                  x1={chartX(month)}
                  y1="546"
                  x2={chartX(month)}
                  y2="558"
                />
                <text className="axis-label" x={chartX(month)} y="592" textAnchor="middle">
                  {month}
                </text>
              </g>
            ))}
            <text className="axis-title" x="584" y="632" textAnchor="middle">
              Months
            </text>
          </svg>
          <p className="chart-caption">Retention estimated from tenure (Kaplan-Meier)</p>
        </article>
      </main>
      <Footer />
    </section>
  );
}

function ActionPlan() {
  return (
    <section className="report-frame">
      <FrameHeader eyebrow="Action plan" title="Retention priorities" />
      <main className="frame-content action-content">
        <article className="risk-callout">
          <div className="risk-label">Highest-risk segment</div>
          <h2>Month-to-month + fiber optic + electronic check</h2>
          <div className="risk-stats">
            <div>
              <strong>1,307</strong>
              <span>customers</span>
            </div>
            <div>
              <strong>60.4%</strong>
              <span>churn</span>
            </div>
            <div>
              <strong>42.2%</strong>
              <span>of all churners</span>
            </div>
          </div>
        </article>
        <div className="recommendations-heading">
          <p className="section-kicker">Recommended actions</p>
          <h2>Five priorities to improve retention</h2>
        </div>
        <div className="recommendation-grid">
          {recommendations.map((recommendation, index) => (
            <article className="recommendation-card" key={recommendation}>
              <span>{index + 1}</span>
              <h3>{recommendation}</h3>
            </article>
          ))}
        </div>
      </main>
      <Footer />
    </section>
  );
}

export default function App() {
  return (
    <div className="report">
      <Overview />
      <ChurnDrivers />
      <CustomerLifetime />
      <ActionPlan />
    </div>
  );
}
