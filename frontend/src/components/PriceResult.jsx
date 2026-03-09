import { TrendingUp, TrendingDown } from "lucide-react";
import FeatureImportanceChart from "./FeatureImportanceChart";

export default function PriceResult({ result }) {
  if (!result) return null;

  const {
    predicted_price,
    confidence_low,
    confidence_high,
    model_name,
    feature_importance,
    currency_symbol = "$",
    currency = "USD",
    city,
  } = result;

  const fmt = (n) => n?.toLocaleString(undefined, { maximumFractionDigits: 0 });

  return (
    <div className="space-y-6 animate-in">
      <div className="card p-8 text-center">
        <p className="text-sm font-medium text-gray-airbnb uppercase tracking-wider mb-2">
          Predicted Nightly Price{city ? ` in ${city}` : ""}
        </p>
        <div className="flex items-center justify-center gap-1">
          <span className="text-airbnb text-3xl font-bold">{currency_symbol}</span>
          <span className="text-6xl font-bold text-dark">
            {fmt(predicted_price)}
          </span>
        </div>
        <p className="text-sm text-gray-airbnb mt-2">per night ({currency})</p>

        <div className="flex items-center justify-center gap-6 mt-6 pt-6 border-t border-gray-100">
          <div className="flex items-center gap-2 text-green-600">
            <TrendingDown size={18} />
            <div className="text-left">
              <p className="text-xs text-gray-airbnb">Low estimate</p>
              <p className="font-semibold">
                {currency_symbol}{fmt(confidence_low)}
              </p>
            </div>
          </div>
          <div className="w-px h-10 bg-gray-200" />
          <div className="flex items-center gap-2 text-orange-600">
            <TrendingUp size={18} />
            <div className="text-left">
              <p className="text-xs text-gray-airbnb">High estimate</p>
              <p className="font-semibold">
                {currency_symbol}{fmt(confidence_high)}
              </p>
            </div>
          </div>
        </div>

        {model_name && (
          <p className="text-xs text-gray-400 mt-4">
            Predicted by {model_name.replace("_tuned", " (tuned)")}
          </p>
        )}
      </div>

      <FeatureImportanceChart data={feature_importance} />
    </div>
  );
}
