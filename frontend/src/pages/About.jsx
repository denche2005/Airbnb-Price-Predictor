import { useEffect, useState } from "react";
import {
  Database,
  Cpu,
  BarChart3,
  Code2,
  Server,
  Layout,
  CheckCircle2,
  Globe2,
} from "lucide-react";
import { getMetrics } from "../services/api";

const techStack = [
  { icon: Cpu, name: "LightGBM / XGBoost / CatBoost", desc: "Gradient boosting models with Optuna Bayesian tuning" },
  { icon: Server, name: "FastAPI", desc: "High-performance Python API backend" },
  { icon: Layout, name: "React + Tailwind", desc: "Modern, responsive frontend" },
  { icon: Database, name: "500K+ Listings", desc: "Real Airbnb data from Inside Airbnb across 24 cities worldwide" },
  { icon: Globe2, name: "6 Continents", desc: "Europe, Americas, Asia, Oceania, Africa — global coverage" },
  { icon: Code2, name: "Playwright", desc: "Automated scraping of any Airbnb listing page" },
  { icon: BarChart3, name: "Recharts", desc: "Interactive feature importance visualizations" },
];

const CITY_LIST = [
  "Amsterdam", "Athens", "Bangkok", "Barcelona", "Berlin",
  "Buenos Aires", "Cape Town", "Chicago", "Hong Kong", "Lisbon",
  "London", "Los Angeles", "Madrid", "Melbourne", "Mexico City",
  "New York", "Paris", "Prague", "Rome", "San Francisco",
  "Singapore", "Sydney", "Tokyo", "Vienna",
];

export default function About() {
  const [metrics, setMetrics] = useState(null);

  useEffect(() => {
    getMetrics().then(setMetrics).catch(() => {});
  }, []);

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="text-center mb-14">
        <h1 className="text-3xl md:text-4xl font-bold text-dark">
          How It Works
        </h1>
        <p className="mt-2 text-gray-airbnb max-w-2xl mx-auto">
          PricebnB uses machine learning to predict Airbnb nightly prices based
          on property characteristics, location, host reputation, reviews, and
          amenities — across 24 cities worldwide.
        </p>
      </div>

      {/* Model Metrics */}
      {metrics && !metrics.error && (
        <div className="card p-8 mb-12">
          <h2 className="text-xl font-semibold text-dark mb-6 flex items-center gap-2">
            <BarChart3 className="text-airbnb" size={22} />
            Model Performance
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <MetricCard
              label="Best Model"
              value={metrics.best_model?.replace("_tuned", "")}
            />
            <MetricCard
              label="Test R² Score"
              value={metrics.test_r2?.toFixed(4)}
            />
            <MetricCard
              label="Test RMSE"
              value={metrics.test_rmse?.toFixed(4)}
            />
            <MetricCard
              label="CV R² (5-fold)"
              value={`${metrics.cv_r2_mean?.toFixed(4)} ± ${metrics.cv_r2_std?.toFixed(4)}`}
            />
          </div>

          {metrics.all_results && (
            <div className="mt-8">
              <h3 className="text-sm font-semibold text-dark mb-3 uppercase tracking-wider">
                All Models Compared
              </h3>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-200">
                      <th className="text-left py-2 pr-4 font-medium text-gray-airbnb">Model</th>
                      <th className="text-right py-2 px-4 font-medium text-gray-airbnb">R²</th>
                      <th className="text-right py-2 px-4 font-medium text-gray-airbnb">RMSE</th>
                      <th className="text-right py-2 pl-4 font-medium text-gray-airbnb">MAE</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(metrics.all_results)
                      .sort(([, a], [, b]) => b.r2 - a.r2)
                      .map(([name, vals]) => (
                        <tr key={name} className="border-b border-gray-50 hover:bg-gray-50">
                          <td className="py-2 pr-4 font-medium text-dark flex items-center gap-1.5">
                            {name === metrics.best_model && (
                              <CheckCircle2 size={14} className="text-green-500" />
                            )}
                            {name.replace("_tuned", " (tuned)")}
                          </td>
                          <td className="text-right py-2 px-4 tabular-nums">{vals.r2?.toFixed(4)}</td>
                          <td className="text-right py-2 px-4 tabular-nums">{vals.rmse?.toFixed(4)}</td>
                          <td className="text-right py-2 pl-4 tabular-nums">{vals.mae?.toFixed(4)}</td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Pipeline Architecture */}
      <div className="card p-8 mb-12">
        <h2 className="text-xl font-semibold text-dark mb-6">ML Pipeline</h2>
        <div className="flex flex-col md:flex-row items-center gap-4 text-sm">
          {[
            { label: "Data Download", sub: "24 cities, Inside Airbnb" },
            { label: "Data Ingestion", sub: "500K+ rows, price & amenity parsing" },
            { label: "Feature Engineering", sub: "45+ features, 3 derived" },
            { label: "Preprocessing", sub: "Impute + Encode + Scale" },
            { label: "Model Training", sub: "9 models + Optuna tuning" },
            { label: "Prediction API", sub: "FastAPI + React UI" },
          ].map((s, i, arr) => (
            <div key={s.label} className="flex items-center gap-4">
              <div className="bg-airbnb/10 rounded-xl p-4 text-center min-w-[140px]">
                <p className="font-semibold text-dark">{s.label}</p>
                <p className="text-xs text-gray-airbnb mt-1">{s.sub}</p>
              </div>
              {i < arr.length - 1 && (
                <span className="text-gray-300 text-xl hidden md:block">&rarr;</span>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Covered Cities */}
      <div className="card p-8 mb-12">
        <h2 className="text-xl font-semibold text-dark mb-6 flex items-center gap-2">
          <Globe2 className="text-airbnb" size={22} />
          Cities Covered
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-2">
          {CITY_LIST.map((city) => (
            <span
              key={city}
              className="bg-gray-50 rounded-lg px-3 py-2 text-sm text-dark text-center font-medium"
            >
              {city}
            </span>
          ))}
        </div>
      </div>

      {/* Features Used */}
      <div className="card p-8 mb-12">
        <h2 className="text-xl font-semibold text-dark mb-6">
          Features Used for Prediction
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="text-sm font-semibold text-dark mb-3 uppercase tracking-wider">
              Numerical (39)
            </h3>
            <ul className="space-y-1.5 text-sm text-gray-airbnb">
              {[
                "accommodates", "bedrooms", "beds", "bathrooms",
                "latitude", "longitude", "amenities_count",
                "host_response_rate", "host_acceptance_rate",
                "number_of_reviews", "reviews_per_month",
                "review_scores_rating + 6 sub-scores",
                "minimum_nights", "availability_365",
                "calculated_host_listings_count",
                "18 amenity binary flags (elevator, pool, ...)",
                "rooms_per_person *", "beds_per_room *", "bath_per_room *",
              ].map((f) => (
                <li key={f} className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 bg-airbnb rounded-full" />
                  {f}
                </li>
              ))}
            </ul>
            <p className="text-xs text-gray-400 mt-2">* engineered features</p>
          </div>
          <div>
            <h3 className="text-sm font-semibold text-dark mb-3 uppercase tracking-wider">
              Categorical (6)
            </h3>
            <ul className="space-y-1.5 text-sm text-gray-airbnb">
              {[
                "property_type",
                "room_type",
                "city (24 worldwide cities)",
                "country (19 countries)",
                "host_is_superhost",
                "instant_bookable",
              ].map((f) => (
                <li key={f} className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 bg-dark rounded-full" />
                  {f}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      {/* Tech Stack */}
      <div className="mb-12">
        <h2 className="text-xl font-semibold text-dark mb-6 text-center">
          Tech Stack
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
          {techStack.map(({ icon: Icon, name, desc }) => (
            <div key={name} className="card p-5 flex items-start gap-4">
              <div className="w-10 h-10 bg-airbnb/10 rounded-lg flex items-center justify-center flex-shrink-0">
                <Icon className="text-airbnb" size={20} />
              </div>
              <div>
                <h3 className="font-semibold text-dark text-sm">{name}</h3>
                <p className="text-xs text-gray-airbnb mt-0.5">{desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function MetricCard({ label, value }) {
  return (
    <div className="bg-gray-50 rounded-xl p-4 text-center">
      <p className="text-xs text-gray-airbnb font-medium uppercase tracking-wider">
        {label}
      </p>
      <p className="text-xl font-bold text-dark mt-1">{value || "\u2014"}</p>
    </div>
  );
}
