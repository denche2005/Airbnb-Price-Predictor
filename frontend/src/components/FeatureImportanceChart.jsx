import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const formatLabel = (name) =>
  name
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());

export default function FeatureImportanceChart({ data }) {
  if (!data || data.length === 0) return null;

  const chartData = data.map((d) => ({
    name: formatLabel(d.feature),
    value: d.importance,
  }));

  return (
    <div className="card p-6">
      <h3 className="text-lg font-semibold text-dark mb-4">
        Feature Importance
      </h3>
      <p className="text-sm text-gray-airbnb mb-6">
        Which factors matter most for pricing
      </p>
      <ResponsiveContainer width="100%" height={350}>
        <BarChart
          data={chartData}
          layout="vertical"
          margin={{ left: 140, right: 16 }}
          barCategoryGap={6}
        >
          <XAxis type="number" tick={{ fontSize: 11 }} />
          <YAxis
            type="category"
            dataKey="name"
            tick={{ fontSize: 11 }}
            width={130}
          />
          <Tooltip
            formatter={(v) => [v.toFixed(4), "Importance"]}
            contentStyle={{
              borderRadius: "8px",
              border: "1px solid #eee",
              fontSize: "13px",
            }}
          />
          <Bar
            dataKey="value"
            radius={[0, 4, 4, 0]}
            fill="#FF385C"
            maxBarSize={22}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
