import { useState, useEffect, useMemo } from "react";
import { ArrowRight, Search } from "lucide-react";
import { getCities } from "../services/api";

const PROPERTY_TYPES = [
  "Entire rental unit", "Private room in rental unit", "Entire condo",
  "Private room in home", "Entire home", "Entire loft",
  "Private room in condo", "Entire serviced apartment",
  "Entire guest suite", "Private room in bed and breakfast",
  "Room in boutique hotel", "Entire townhouse", "Entire villa",
  "Private room in townhouse", "Room in hotel",
  "Shared room in rental unit", "Entire cabin", "Entire bungalow",
  "Entire cottage", "Boat", "Tiny home", "Camper/RV", "Treehouse",
  "Other",
];
const ROOM_TYPES = ["Entire home/apt", "Private room", "Shared room", "Hotel room"];

const AMENITY_TOGGLES = [
  { key: "has_elevator", label: "Elevator" },
  { key: "has_pool", label: "Pool" },
  { key: "has_hot_tub", label: "Hot Tub" },
  { key: "has_gym", label: "Gym" },
  { key: "has_doorman", label: "Doorman" },
  { key: "has_air_conditioning", label: "A/C" },
  { key: "has_heating", label: "Heating" },
  { key: "has_washer", label: "Washer" },
  { key: "has_dryer", label: "Dryer" },
  { key: "has_kitchen", label: "Kitchen" },
  { key: "has_tv", label: "TV" },
  { key: "has_wifi", label: "WiFi" },
  { key: "has_free_parking_on_premises", label: "Free Parking" },
  { key: "has_indoor_fireplace", label: "Fireplace" },
  { key: "has_patio_or_balcony", label: "Patio / Balcony" },
  { key: "has_breakfast", label: "Breakfast" },
  { key: "has_buzzer_wireless_intercom", label: "Buzzer / Intercom" },
  { key: "has_wheelchair_accessible", label: "Wheelchair Access" },
];

const DEFAULT_FORM = {
  property_type: "Entire rental unit",
  room_type: "Entire home/apt",
  city: "New York",
  accommodates: 2,
  bedrooms: 1,
  beds: 1,
  bathrooms: 1,
  amenities_count: 20,
  host_response_rate: 90,
  host_acceptance_rate: 85,
  host_is_superhost: "f",
  instant_bookable: "f",
  number_of_reviews: 10,
  reviews_per_month: 1.5,
  review_scores_rating: 4.5,
  review_scores_accuracy: 4.5,
  review_scores_cleanliness: 4.5,
  review_scores_checkin: 4.5,
  review_scores_communication: 4.5,
  review_scores_location: 4.5,
  review_scores_value: 4.5,
  minimum_nights: 2,
  availability_365: 200,
  calculated_host_listings_count: 1,
  ...Object.fromEntries(AMENITY_TOGGLES.map((a) => [a.key, 0])),
};

function Select({ label, name, options, value, onChange }) {
  return (
    <div>
      <label className="block text-sm font-medium text-dark mb-1">{label}</label>
      <select name={name} value={value} onChange={onChange} className="input-field">
        {options.map((o) => (
          <option key={o} value={o}>{o}</option>
        ))}
      </select>
    </div>
  );
}

function NumberInput({ label, name, value, onChange, min, max, step }) {
  return (
    <div>
      <label className="block text-sm font-medium text-dark mb-1">{label}</label>
      <input
        type="number"
        name={name}
        value={value}
        onChange={onChange}
        min={min}
        max={max}
        step={step || 1}
        className="input-field"
      />
    </div>
  );
}

function Toggle({ label, name, value, onChange }) {
  const isOn = value === "t";
  return (
    <div className="flex items-center justify-between">
      <label className="text-sm font-medium text-dark">{label}</label>
      <button
        type="button"
        onClick={() => onChange({ target: { name, value: isOn ? "f" : "t", type: "text" } })}
        className={`relative w-11 h-6 rounded-full transition-colors ${
          isOn ? "bg-airbnb" : "bg-gray-300"
        }`}
      >
        <span
          className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform ${
            isOn ? "translate-x-5" : ""
          }`}
        />
      </button>
    </div>
  );
}

export default function PredictionForm({ onSubmit, loading }) {
  const [form, setForm] = useState(DEFAULT_FORM);
  const [cityData, setCityData] = useState(null);
  const [citySearch, setCitySearch] = useState("");
  const [showCityDropdown, setShowCityDropdown] = useState(false);

  useEffect(() => {
    getCities().then(setCityData).catch(() => {});
  }, []);

  const cities = useMemo(() => {
    if (!cityData?.cities) return ["New York"];
    return cityData.cities;
  }, [cityData]);

  const filteredCities = useMemo(() => {
    if (!citySearch.trim()) return cities;
    const q = citySearch.toLowerCase();
    return cities.filter((c) => c.toLowerCase().includes(q));
  }, [cities, citySearch]);

  const handleChange = (e) => {
    const { name, value, type } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: type === "number" ? Number(value) : value,
    }));
  };

  const selectCity = (city) => {
    setForm((prev) => ({ ...prev, city }));
    setCitySearch("");
    setShowCityDropdown(false);
  };

  const toggleAmenity = (key) => {
    setForm((prev) => ({ ...prev, [key]: prev[key] === 1 ? 0 : 1 }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const data = { ...form };
    if (cityData?.city_coords?.[form.city]) {
      const [lat, lng] = cityData.city_coords[form.city];
      data.latitude = lat;
      data.longitude = lng;
    }
    if (cityData?.city_currency) {
      const countryMap = {
        "Amsterdam": "Netherlands", "Athens": "Greece", "Bangkok": "Thailand",
        "Barcelona": "Spain", "Berlin": "Germany", "Buenos Aires": "Argentina",
        "Cape Town": "South Africa", "Chicago": "United States",
        "Hong Kong": "China", "Lisbon": "Portugal", "London": "United Kingdom",
        "Los Angeles": "United States", "Madrid": "Spain",
        "Melbourne": "Australia", "Mexico City": "Mexico",
        "New York": "United States", "Paris": "France", "Prague": "Czech Republic",
        "Rome": "Italy", "San Francisco": "United States",
        "Singapore": "Singapore", "Sydney": "Australia",
        "Tokyo": "Japan", "Vienna": "Austria",
      };
      data.country = countryMap[form.city] || "United States";
    }
    onSubmit(data);
  };

  const currencyForCity = cityData?.city_currency?.[form.city] || "USD";
  const currencySymbol = cityData?.currency_symbols?.[currencyForCity] || "$";

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* City & Property */}
      <fieldset>
        <legend className="text-base font-semibold text-dark mb-3 pb-2 border-b border-gray-100">
          Location &amp; Property
        </legend>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="relative">
            <label className="block text-sm font-medium text-dark mb-1">City</label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={16} />
              <input
                type="text"
                value={showCityDropdown ? citySearch : form.city}
                onFocus={() => { setShowCityDropdown(true); setCitySearch(""); }}
                onBlur={() => setTimeout(() => setShowCityDropdown(false), 200)}
                onChange={(e) => setCitySearch(e.target.value)}
                className="input-field pl-9"
                placeholder="Search cities..."
              />
            </div>
            {showCityDropdown && (
              <div className="absolute z-20 w-full mt-1 bg-white border border-gray-200 rounded-xl shadow-lg max-h-60 overflow-y-auto">
                {filteredCities.map((c) => (
                  <button
                    key={c}
                    type="button"
                    onMouseDown={() => selectCity(c)}
                    className={`w-full text-left px-4 py-2.5 text-sm hover:bg-airbnb/5 transition-colors ${
                      form.city === c ? "bg-airbnb/10 font-medium text-airbnb" : "text-dark"
                    }`}
                  >
                    {c}
                    <span className="text-xs text-gray-400 ml-2">
                      {cityData?.city_currency?.[c] || ""}
                    </span>
                  </button>
                ))}
                {filteredCities.length === 0 && (
                  <p className="px-4 py-3 text-sm text-gray-400">No cities found</p>
                )}
              </div>
            )}
            {form.city && (
              <p className="text-xs text-gray-400 mt-1">
                Currency: {currencySymbol} ({currencyForCity})
              </p>
            )}
          </div>

          <Select label="Property Type" name="property_type" options={PROPERTY_TYPES} value={form.property_type} onChange={handleChange} />
          <Select label="Room Type" name="room_type" options={ROOM_TYPES} value={form.room_type} onChange={handleChange} />
          <NumberInput label="Bedrooms" name="bedrooms" value={form.bedrooms} onChange={handleChange} min={0} max={20} />
          <NumberInput label="Beds" name="beds" value={form.beds} onChange={handleChange} min={0} max={30} />
          <NumberInput label="Bathrooms" name="bathrooms" value={form.bathrooms} onChange={handleChange} min={0} max={10} step={0.5} />
          <NumberInput label="Accommodates" name="accommodates" value={form.accommodates} onChange={handleChange} min={1} max={30} />
          <NumberInput label="Min. Nights" name="minimum_nights" value={form.minimum_nights} onChange={handleChange} min={1} max={365} />
          <NumberInput label="Availability (days/year)" name="availability_365" value={form.availability_365} onChange={handleChange} min={0} max={365} />
        </div>
      </fieldset>

      {/* Amenities */}
      <fieldset>
        <legend className="text-base font-semibold text-dark mb-3 pb-2 border-b border-gray-100">
          Amenities
        </legend>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-2">
          {AMENITY_TOGGLES.map(({ key, label }) => (
            <button
              key={key}
              type="button"
              onClick={() => toggleAmenity(key)}
              className={`px-3 py-2 rounded-full text-sm font-medium border transition-all ${
                form[key] === 1
                  ? "bg-airbnb text-white border-airbnb"
                  : "bg-white text-gray-600 border-gray-300 hover:border-gray-400"
              }`}
            >
              {label}
            </button>
          ))}
        </div>
        <div className="mt-3 max-w-xs">
          <NumberInput label="Total Amenities Count" name="amenities_count" value={form.amenities_count} onChange={handleChange} min={0} max={100} />
        </div>
      </fieldset>

      {/* Host Details */}
      <fieldset>
        <legend className="text-base font-semibold text-dark mb-3 pb-2 border-b border-gray-100">
          Host Details
        </legend>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <NumberInput label="Host Response Rate (%)" name="host_response_rate" value={form.host_response_rate} onChange={handleChange} min={0} max={100} />
          <NumberInput label="Host Acceptance Rate (%)" name="host_acceptance_rate" value={form.host_acceptance_rate} onChange={handleChange} min={0} max={100} />
          <NumberInput label="Host Listings Count" name="calculated_host_listings_count" value={form.calculated_host_listings_count} onChange={handleChange} min={0} />
          <Toggle label="Superhost" name="host_is_superhost" value={form.host_is_superhost} onChange={handleChange} />
          <Toggle label="Instant Bookable" name="instant_bookable" value={form.instant_bookable} onChange={handleChange} />
        </div>
      </fieldset>

      {/* Reviews */}
      <fieldset>
        <legend className="text-base font-semibold text-dark mb-3 pb-2 border-b border-gray-100">
          Reviews
        </legend>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <NumberInput label="Number of Reviews" name="number_of_reviews" value={form.number_of_reviews} onChange={handleChange} min={0} />
          <NumberInput label="Reviews / Month" name="reviews_per_month" value={form.reviews_per_month} onChange={handleChange} min={0} step={0.1} />
          <NumberInput label="Overall Rating (0-5)" name="review_scores_rating" value={form.review_scores_rating} onChange={handleChange} min={0} max={5} step={0.1} />
          <NumberInput label="Accuracy (0-5)" name="review_scores_accuracy" value={form.review_scores_accuracy} onChange={handleChange} min={0} max={5} step={0.1} />
          <NumberInput label="Cleanliness (0-5)" name="review_scores_cleanliness" value={form.review_scores_cleanliness} onChange={handleChange} min={0} max={5} step={0.1} />
          <NumberInput label="Check-in (0-5)" name="review_scores_checkin" value={form.review_scores_checkin} onChange={handleChange} min={0} max={5} step={0.1} />
          <NumberInput label="Communication (0-5)" name="review_scores_communication" value={form.review_scores_communication} onChange={handleChange} min={0} max={5} step={0.1} />
          <NumberInput label="Location (0-5)" name="review_scores_location" value={form.review_scores_location} onChange={handleChange} min={0} max={5} step={0.1} />
          <NumberInput label="Value (0-5)" name="review_scores_value" value={form.review_scores_value} onChange={handleChange} min={0} max={5} step={0.1} />
        </div>
      </fieldset>

      <button type="submit" className="btn-primary w-full gap-2" disabled={loading}>
        {loading ? "Predicting..." : "Predict Price"}
        {!loading && <ArrowRight size={18} />}
      </button>
    </form>
  );
}
