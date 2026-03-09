import { Link } from "react-router-dom";
import {
  Brain,
  Zap,
  Globe2,
  ArrowRight,
  BarChart3,
  Link2,
  ClipboardList,
} from "lucide-react";

const features = [
  {
    icon: Brain,
    title: "ML-Powered",
    desc: "LightGBM & XGBoost models tuned with Bayesian optimization on 500K+ real listings worldwide.",
  },
  {
    icon: Zap,
    title: "Instant Results",
    desc: "Get a price estimate in seconds — paste a link or fill out a quick form.",
  },
  {
    icon: Globe2,
    title: "24+ Cities Worldwide",
    desc: "From New York to Tokyo, Barcelona to Sydney — global coverage across 6 continents.",
  },
];

const steps = [
  {
    icon: Link2,
    step: "1",
    title: "Paste an Airbnb URL",
    desc: "Or manually enter listing details like bedrooms, city, and amenities.",
  },
  {
    icon: BarChart3,
    step: "2",
    title: "ML Model Analyzes",
    desc: "Our tuned model evaluates 45+ features to estimate the fair nightly rate in local currency.",
  },
  {
    icon: ClipboardList,
    step: "3",
    title: "Get Your Estimate",
    desc: "See the predicted price, confidence range, and which features matter most.",
  },
];

export default function Home() {
  return (
    <>
      {/* Hero */}
      <section className="relative overflow-hidden bg-gradient-to-br from-airbnb via-airbnb-dark to-pink-900">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGRlZnM+PHBhdHRlcm4gaWQ9ImciIHdpZHRoPSI2MCIgaGVpZ2h0PSI2MCIgcGF0dGVyblVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+PHBhdGggZD0iTTAgMGg2MHY2MEgweiIgZmlsbD0ibm9uZSIvPjxjaXJjbGUgY3g9IjMwIiBjeT0iMzAiIHI9IjEiIGZpbGw9InJnYmEoMjU1LDI1NSwyNTUsMC4wNSkiLz48L3BhdHRlcm4+PC9kZWZzPjxyZWN0IGZpbGw9InVybCgjZykiIHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiLz48L3N2Zz4=')] opacity-50" />
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 md:py-32">
          <div className="max-w-3xl mx-auto text-center">
            <h1 className="text-4xl md:text-6xl font-extrabold text-white leading-tight">
              Predict Any Airbnb
              <br />
              <span className="text-pink-200">Listing Price Worldwide</span>
            </h1>
            <p className="mt-6 text-lg md:text-xl text-pink-100 max-w-2xl mx-auto">
              Powered by machine learning trained on 500,000+ real Airbnb
              listings across 24 cities on 6 continents. Get instant,
              data-driven price estimates in local currency.
            </p>
            <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link to="/predict" className="btn-primary bg-white text-airbnb hover:bg-gray-100 gap-2 text-lg px-8 py-4">
                Start Predicting
                <ArrowRight size={20} />
              </Link>
              <Link to="/about" className="btn-outline border-white text-white hover:bg-white/10 hover:text-white px-8 py-4">
                How It Works
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center mb-14">
          <h2 className="text-3xl font-bold text-dark">Why PricebnB?</h2>
          <p className="mt-3 text-gray-airbnb max-w-xl mx-auto">
            Combining cutting-edge ML with an intuitive interface to make Airbnb
            pricing transparent — anywhere in the world.
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {features.map(({ icon: Icon, title, desc }) => (
            <div key={title} className="card p-8 text-center">
              <div className="w-14 h-14 bg-airbnb/10 rounded-2xl flex items-center justify-center mx-auto mb-5">
                <Icon className="text-airbnb" size={28} />
              </div>
              <h3 className="text-lg font-semibold text-dark mb-2">{title}</h3>
              <p className="text-gray-airbnb text-sm leading-relaxed">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section className="bg-gray-50 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-bold text-dark">How It Works</h2>
            <p className="mt-3 text-gray-airbnb">Three simple steps to your price estimate</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {steps.map(({ icon: Icon, step, title, desc }) => (
              <div key={step} className="flex flex-col items-center text-center">
                <div className="relative mb-6">
                  <div className="w-16 h-16 bg-airbnb rounded-full flex items-center justify-center">
                    <Icon className="text-white" size={28} />
                  </div>
                  <span className="absolute -top-2 -right-2 w-7 h-7 bg-dark text-white text-xs font-bold rounded-full flex items-center justify-center">
                    {step}
                  </span>
                </div>
                <h3 className="text-lg font-semibold text-dark mb-2">{title}</h3>
                <p className="text-gray-airbnb text-sm leading-relaxed max-w-xs">
                  {desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="card bg-gradient-to-r from-airbnb to-airbnb-dark p-12 text-center">
          <h2 className="text-3xl font-bold text-white">Ready to predict?</h2>
          <p className="mt-3 text-pink-100 max-w-lg mx-auto">
            Whether you're a host setting rates or a traveler checking if a deal
            is fair — try it now with any listing worldwide.
          </p>
          <Link to="/predict" className="btn-primary bg-white text-airbnb hover:bg-gray-100 mt-8 gap-2 text-lg px-8 py-4 inline-flex">
            Open Price Predictor
            <ArrowRight size={20} />
          </Link>
        </div>
      </section>
    </>
  );
}
