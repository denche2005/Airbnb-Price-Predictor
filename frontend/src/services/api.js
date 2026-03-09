import axios from "axios";

const api = axios.create({ baseURL: "/api" });

export async function predictPrice(data) {
  const res = await api.post("/predict", data);
  return res.data;
}

export async function scrapeAndPredict(url) {
  const res = await api.post("/scrape", { url });
  return res.data;
}

export async function getMetrics() {
  const res = await api.get("/metrics");
  return res.data;
}

export async function healthCheck() {
  const res = await api.get("/health");
  return res.data;
}

export async function getCities() {
  const res = await api.get("/cities");
  return res.data;
}
