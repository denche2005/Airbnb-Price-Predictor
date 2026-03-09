import { useState } from "react";
import { Link2, ArrowRight, AlertCircle } from "lucide-react";

export default function URLInput({ onSubmit, loading }) {
  const [url, setUrl] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    setError("");
    if (!url.trim()) {
      setError("Please enter an Airbnb URL");
      return;
    }
    if (!/airbnb\.[a-z.]+\/rooms\/\d+/i.test(url)) {
      setError("Please enter a valid Airbnb listing URL (e.g. airbnb.com/rooms/12345 or airbnb.es/rooms/...)");
      return;
    }
    onSubmit(url.trim());
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-dark mb-2">
          Airbnb Listing URL
        </label>
        <div className="relative">
          <Link2
            className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400"
            size={18}
          />
          <input
            type="url"
            value={url}
            onChange={(e) => {
              setUrl(e.target.value);
              setError("");
            }}
            placeholder="https://www.airbnb.com/rooms/12345678"
            className="input-field pl-11 pr-4"
            disabled={loading}
          />
        </div>
        {error && (
          <div className="flex items-center gap-1.5 mt-2 text-red-500 text-sm">
            <AlertCircle size={14} />
            <span>{error}</span>
          </div>
        )}
      </div>

      <p className="text-xs text-gray-airbnb">
        We'll automatically extract the listing details and predict its fair
        price. Scraping may take a few seconds.
      </p>

      <button type="submit" className="btn-primary w-full gap-2" disabled={loading}>
        {loading ? "Scraping & Analyzing..." : "Analyze Listing"}
        {!loading && <ArrowRight size={18} />}
      </button>
    </form>
  );
}
