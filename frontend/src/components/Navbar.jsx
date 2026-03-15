import { Link, useLocation } from "react-router-dom";
import { Home, BarChart3, Info } from "lucide-react";

const links = [
  { to: "/", label: "Home", icon: Home },
  { to: "/predict", label: "Predict", icon: BarChart3 },
  { to: "/about", label: "About", icon: Info },
];

export default function Navbar() {
  const { pathname } = useLocation();

  return (
    <header className="sticky top-0 z-50 bg-white/90 backdrop-blur border-b border-gray-200">
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2 group">
          <img
            src="/logo.png"
            alt="Airbnb Predictor"
            className="h-10 w-auto object-contain"
          />
        </Link>

        <ul className="flex items-center gap-1 bg-gray-100 rounded-full px-1 py-1">
          {links.map(({ to, label, icon: Icon }) => {
            const active = pathname === to;
            return (
              <li key={to}>
                <Link
                  to={to}
                  className={`flex items-center gap-1.5 px-4 py-1.5 rounded-full text-sm font-medium transition-all ${
                    active
                      ? "bg-white text-dark shadow-sm"
                      : "text-gray-airbnb hover:bg-white hover:text-dark"
                  }`}
                >
                  <Icon size={16} />
                  <span className="hidden sm:inline">{label}</span>
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>
    </header>
  );
}
