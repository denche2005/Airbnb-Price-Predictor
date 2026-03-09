import { useState } from "react";
import { Link2, ClipboardList, AlertCircle } from "lucide-react";
import URLInput from "../components/URLInput";
import PredictionForm from "../components/PredictionForm";
import PriceResult from "../components/PriceResult";
import LoadingSpinner from "../components/LoadingSpinner";
import { predictPrice, scrapeAndPredict } from "../services/api";

const TABS = [
  { id: "url", label: "Paste URL", icon: Link2 },
  { id: "form", label: "Manual Input", icon: ClipboardList },
];

export default function Predictor() {
  const [tab, setTab] = useState("url");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const handleURL = async (url) => {
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const data = await scrapeAndPredict(url);
      setResult(data);
    } catch (err) {
      const msg =
        err.response?.data?.detail ||
        "Scraping failed. Try the manual form instead.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleForm = async (formData) => {
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const data = await predictPrice(formData);
      setResult(data);
    } catch (err) {
      const msg =
        err.response?.data?.detail || "Prediction failed. Please try again.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="mb-10 flex flex-col md:flex-row md:items-end md:justify-between gap-4">
        <div>
          <h1 className="text-3xl md:text-4xl font-bold text-dark tracking-tight">
            Check a listing's price
          </h1>
          <p className="mt-2 text-gray-airbnb max-w-xl">
            Paste an Airbnb URL or enter the details of a stay to see what our
            worldwide model thinks is a fair nightly rate.
          </p>
        </div>
        <div className="hidden md:flex items-center gap-2 text-xs text-gray-airbnb bg-gray-50 rounded-full px-3 py-1.5 border border-gray-200">
          <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
          <span>Model trained on 500K+ listings · 24 cities</span>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex justify-center mb-8">
        <div className="inline-flex bg-gray-100 rounded-xl p-1">
          {TABS.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => {
                setTab(id);
                setError("");
              }}
              className={`flex items-center gap-2 px-6 py-2.5 rounded-lg text-sm font-medium transition-all ${
                tab === id
                  ? "bg-white text-dark shadow-sm"
                  : "text-gray-airbnb hover:text-dark"
              }`}
            >
              <Icon size={16} />
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* Input + side copy */}
      <div className="grid grid-cols-1 lg:grid-cols-[minmax(0,3fr)_minmax(0,2fr)] gap-8 mb-10">
        <div className="card p-6 sm:p-8">
          {tab === "url" ? (
            <URLInput onSubmit={handleURL} loading={loading} />
          ) : (
            <PredictionForm onSubmit={handleForm} loading={loading} />
          )}
        </div>
        <div className="hidden lg:block">
          <div className="rounded-3xl overflow-hidden border border-gray-200 shadow-sm bg-gradient-to-br from-gray-50 to-white h-full flex flex-col">
            <div className="h-40 bg-[radial-gradient(circle_at_top,_#FF385C33,_transparent_55%)] flex items-center justify-center border-b border-gray-200">
              <div className="w-40 h-24 rounded-3xl bg-white shadow-md border border-gray-200 flex flex-col justify-between p-3">
                <div className="flex items-center justify-between text-[11px] text-gray-airbnb">
                  <span className="font-semibold text-dark">Entire home in</span>
                  <span className="px-2 py-0.5 rounded-full bg-gray-100 text-[10px]">
                    pricebnb
                  </span>
                </div>
                <div>
                  <p className="text-xs text-gray-airbnb mb-1">Tonight's price</p>
                  <p className="text-lg font-bold text-dark">
                    <span className="text-airbnb text-base align-baseline">$</span>
                    180
                    <span className="text-xs font-normal text-gray-airbnb"> / night</span>
                  </p>
                </div>
              </div>
            </div>
            <div className="flex-1 p-5 flex flex-col justify-between">
              <div>
                <h2 className="text-sm font-semibold text-dark mb-2">
                  How this works
                </h2>
                <ul className="space-y-1.5 text-xs text-gray-airbnb">
                  <li>· We scrape high–level details from the listing page.</li>
                  <li>· The worldwide model compares it to 500K+ similar stays.</li>
                  <li>· You see a fair price in the listing's local currency.</li>
                </ul>
              </div>
              <p className="mt-4 text-[11px] text-gray-400">
                This tool is for educational purposes and not affiliated with Airbnb.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="flex items-start gap-3 p-4 mb-8 bg-red-50 border border-red-200 rounded-xl text-red-700">
          <AlertCircle size={20} className="mt-0.5 flex-shrink-0" />
          <div>
            <p className="font-medium">Something went wrong</p>
            <p className="text-sm mt-1">{error}</p>
          </div>
        </div>
      )}

      {/* Loading */}
      {loading && <LoadingSpinner text={tab === "url" ? "Scraping listing & predicting..." : "Running prediction model..."} />}

      {/* Results */}
      {result && !loading && <PriceResult result={result} />}

      {/* Extracted data preview */}
      {result?.extracted_data && (
        <div className="card p-6 mt-6">
          <h3 className="text-lg font-semibold text-dark mb-4">
            Extracted Listing Data
          </h3>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
            {Object.entries(result.extracted_data).map(([k, v]) => (
              <div key={k} className="bg-gray-50 rounded-lg p-3">
                <p className="text-xs text-gray-airbnb capitalize">
                  {k.replace(/_/g, " ")}
                </p>
                <p className="text-sm font-medium text-dark mt-0.5 truncate">
                  {String(v)}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
